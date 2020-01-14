"""
Data update script - fetches player's attributes, latest price and pgp data.
"""

import pandas as pd
import numpy as np 

# other
from datetime import datetime
import os

# scraping
from bs4 import BeautifulSoup
from lxml import html, etree
from urllib.request import urlopen
import json
import requests

# multiprocessing
from multiprocessing import Pool
from tqdm import tqdm


cols = ['player_id', 'player_name', 'overall', 'quality', 'resource_id', 'position', 
            'num_games', 'avg_goals', 'avg_assists','club', 'nationality', 'league', 'skill_moves',
            'weak_foot', 'intl_rep', 'pref_foot', 'height', 'weight', 'revision', 
            'def_workrate', 'att_workrate', 'added_date', 'origin', 'age', 'pace', 'pace_acceleration', 
            'pace_sprint_speed', 'shooting', 'shoot_positioning', 'shoot_finishing', 
            'shoot_shot_power', 'shoot_long_shots', 'shoot_volleys', 'shoot_penalties', 
            'passing', 'pass_vision', 'pass_crossing', 'pass_free_kick', 'pass_short', 
            'pass_long', 'pass_curve', 'dribbling', 'drib_agility', 'drib_balance', 
            'drib_reactions', 'drib_ball_control', 'drib_dribbling', 'drib_composure', 
            'defending', 'def_interceptions', 'def_heading', 'def_marking', 'def_stand_tackle',
            'def_slid_tackle', 'physicality', 'phys_jumping', 'phys_stamina', 'phys_strength', 
            'phys_aggression', 'price']


def fetch_player_soup(player_id):
    """
    Fetch the request and process it with bs4
    Arguments:
        - player_id: Player's ID, int
    Returns:
        - soup: parsed request
    """

    resp = requests.get('https://www.futbin.com/20/player/' + str(player_id))
    soup = BeautifulSoup(resp.text, features='lxml')
    return soup



def fetch_price(resource_id):
    """
    Fetch the latest price for a specific player
    Arguments:
        - resource_id: Player's resource ID, int
    Returns:
        - price: player's latest price, int
    """

    url = 'https://www.futbin.com/20/playerGraph?type=daily_graph&year=20&player=' + str(resource_id)
    resp = requests.get(url)
    price_soup = BeautifulSoup(resp.text, features='lxml')

    try:
        price_data = json.loads(price_soup.text)['ps']
        latest_price = price_data[-1][1]

    except:
        latest_price = 0

    return latest_price



def fetch_player(player_id):
    """
    Fetch all relevant data on a particular player. 
    Arguments:
        - player_id: int, player's ID
    Returns:
        - data: array, contains all requested attributes
    """

    soup = fetch_player_soup(player_id)

    data = [player_id]

    # exception in case there's no player at this ID
    try:
        player_name = soup.find('span', {'class': 'header_name'}).text
    except:
        for j in range(56):
            data.append(0)
        return data

    data.append(player_name)
    data.append(soup.find('h1', {'class': 'player_header header_top pb-0'}).text.strip()[:2])
    data.append(soup.find('div', {'id': 'Player-card'})['class'][-3] + ' ' + \
                      soup.find('div', {'id': 'Player-card'})['class'][-2])

    resource_id = soup.find('div', {'id': 'page-info'})['data-player-resource']
    data.append(resource_id)
    position = soup.find('div', {'id': 'page-info'})['data-position']
    data.append(position)

    if position == 'GK':
        for j in range(52):
            data.append(0)
        return data

    # PGP
    player_stats = soup.findAll('div', {'class': 'ps4-pgp-data'})
    data.append(player_stats[-1].text.split()[-1])
    data.append(player_stats[-2].text.split()[-1])
    data.append(player_stats[-3].text.split()[-1])


    # information
    info = soup.findAll('td', {'class': 'table-row-text'})

    # some are missing international reputation
    try:
        age = info[16].text.strip()
        for i in range(1, 15):
            if i == 8:
                stat = info[i].text.strip()[:3]
            else:
                stat = info[i].text.strip()

            data.append(stat)
        data.append(age)
    except:
        for i in range(1, 6):
            stat = info[i].text.strip()
            data.append(stat)
        stat = 0
        data.append(stat)
        for i in range(6, 14):
            if i == 7:
                stat = info[i].text.strip()[:3]
            else:
                stat = info[i].text.strip()
            data.append(stat)
        data.append(info[15].text.strip())


    # attributes
    stats = json.loads(soup.find('div', {'id': 'player_stats_json'}).text.strip())

    ## PACE
    for i in range(3):
        stat = stats[0]['pace'][i]['value']
        data.append(stat)

    ## SHOOTING
    for i in range(7):
        stat = stats[0]['shooting'][i]['value']
        data.append(stat)

    ## PASSING
    for i in range(7):
        stat = stats[0]['passing'][i]['value']
        data.append(stat)

    ## DRIBBLING
    for i in range(7):
        stat = stats[0]['dribbling'][i]['value']
        data.append(stat)

    ## DEFENDING
    for i in range(6):
        stat = stats[0]['defending'][i]['value']
        data.append(stat)

    ## PHYSICAL
    for i in range(5):
        stat = stats[0]['physical'][i]['value']
        data.append(stat)

    # price
    price = fetch_price(resource_id)
    data.append(price)

    return data



def fetch_latest_pid():
    """
    Find the latest player id 
    """
    resp = requests.get('https://www.futbin.com/latest')
    soup = BeautifulSoup(resp.text, 'lxml')
    pid = soup.find_all('table')[0].find('a').attrs['href'].split('/')[3]
    return int(pid)



def update_player(player_id):
    """
    Fetch a player's PGP data and their latest price
    Arguments:
        - player_id: Player's ID, int
    Returns:
        - data: an array containing their statistics
    """

    soup = fetch_player_soup(player_id)
    resource_id = soup.find('div', {'id': 'page-info'})['data-player-resource']
    data = [player_id]

    # PGP
    player_stats = soup.findAll('div', {'class': 'ps4-pgp-data'})
    data.append(player_stats[-1].text.split()[-1])
    data.append(player_stats[-2].text.split()[-1])
    data.append(player_stats[-3].text.split()[-1])

    # Price
    price = fetch_price(resource_id)
    data.append(price)

    return data


def fetch_new_players(num_processes=10):
    """
    Add new players to our dataframe
    """

    latest_pid = fetch_latest_pid()


    if os.path.exists('data/fifa20.pkl'):
        df = pd.read_pickle('data/fifa20.pkl')
        current_pid = df.player_id.values[-1]

    else:
        df = pd.DataFrame(columns=cols)
        current_pid = 0

    total_pids = latest_pid - current_pid
    pids = range(current_pid+1, latest_pid+1)

    with Pool(num_processes) as p:
        players_data = list(tqdm(p.imap(fetch_player, pids), total=total_pids))

    if df.shape[0] == 0:
        df = pd.DataFrame(data=players_data, columns=cols)
    else:
        new_df = pd.DataFrame(data=players_data, columns=cols)
        df = df.append(new_df)

    df.sort_values(by='player_id', ascending=True, inplace=True)

    return df



def update_df(df, num_processes=10):
    """
    Update a dataframe's pgp and price data
    """

    update_cols = ['num_games', 'avg_goals', 'avg_assists', 'price']       
    df.drop(update_cols, axis=1, inplace=True)

    pids = df.player_id.values
    latest_pid = max(pids)

    total_pids = len(pids)
    pids_range = range(1, latest_pid+1)

    with Pool(num_processes) as p:
        update_data = list(tqdm(p.imap(update_player, pids), total=total_pids))

    # Add the updated data to our dataframe
    update_cols.insert(0, 'player_id')
    df_update = pd.DataFrame(data=update_data, columns=update_cols)
    df = df.merge(df_update, on='player_id', how='left')
    df = df[cols]

    return df


def processing(df):
    """
    Some feature engineering and data cleaning 
    """

    # Fix some dtypes
    stats_cols = ['num_games', 'avg_goals', 'avg_assists', 'overall']
    for col in stats_cols:
        if col == 'num_games':
            df[col] = df[col].str.replace(',', '')
        df[col] = np.where(df[col] == '-', 0, df[col])
        df[col] = pd.to_numeric(df[col])

    # Drop quality
    df.drop('quality', axis=1, inplace=True)

    # Create an average contributions variable
    df['avg_contributions'] = df.avg_goals + df.avg_assists

    return df



if __name__ == '__main__':

    if os.path.exists('data/fifa20.pkl'):
        update = True
    else:
        update = False

    ########## TEMPORARILY OVERRIDING UPDATE
    update = False

    df = fetch_new_players()
    print('Finished fetching new players.')

    if update:
        df = update_df(df)
        print('Finished updating dataframe.')

    df.to_pickle('data/fifa20.pkl')
    print('Saved the dataframe.\n')

    df = processing(df)
    print('Finished processing the dataframe.')

    df.to_pickle('data/fifa20_dash.pkl')
    print('Saved the processed dataframe.\n')
