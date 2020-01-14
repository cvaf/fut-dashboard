import pandas as pd
import numpy as np
from datetime import datetime, timedelta

df_p = pd.read_csv('data/prices_database.csv', index_col='Unnamed: 0', parse_dates=['date', 'added_date'])
stats_cols = ['num_games', 'avg_goals', 'avg_assists'] 
for col in stats_cols:
    if col == 'num_games':
        df_p[col] = df_p[col].str.replace(',', '')
    df_p[col] = np.where(df_p[col] == '-', 0, df_p[col])
    df_p[col] = pd.to_numeric(df_p[col])

    
# drop quality
df_p.drop(['quality'], axis = 1, inplace = True)


# Feature Engineering: general_position variable
attacker_positions = ['LM', 'LW', 'LF', 'CF', 'ST', 'RM', 'RW', 'RF', 'CAM']
midfielder_positions = ['CDM', 'CM']
defender_positions = ['LWB', 'LB', 'CB', 'RWB', 'RB']
df_p['general_position'] = np.nan
df_p['general_position'] = np.where(df_p['position'].isin(attacker_positions), 'Attacker', df_p.general_position)
df_p['general_position'] = np.where(df_p['position'].isin(midfielder_positions), 'Midfielder', df_p.general_position)
df_p['general_position'] = np.where(df_p['position'].isin(defender_positions), 'Defender', df_p.general_position)


# Feature Engineering: Days
df_p['days_available'] = (df_p.date - df_p.added_date).dt.days
df_p['days_since_launch'] = (df_p.date - df_p.date.min()).dt.days
df_p['weekday'] = df_p['date'].dt.weekday_name


# Feature Engineering: Popular Nations
p_ = df_p[['resource_id', 'revision', 'nationality']].groupby('resource_id').last().groupby('nationality').count().sort_values(by=['revision'], ascending = False).reset_index()['nationality'][:10]
popular_nations = list(p_)
df_p['popular_nations'] = np.where(df_p.nationality.isin(popular_nations), 1, 0)


# Feature Engineering: Popular Leagues
p_ = df_p[['resource_id', 'revision', 'league']].groupby('resource_id').last().groupby('league').count().sort_values(by=['revision'], ascending = False).reset_index()['league'][:10]
popular_leagues = list(p_)
df_p['popular_leagues'] = np.where(df_p.league.isin(popular_leagues), 1, 0)



# Output
df_p.to_csv('data/dash_players_dataframe.csv')
df_pe = df_p.groupby('resource_id').last().reset_index()
df_pe['avg_contributions'] = df_pe.avg_goals + df_pe.avg_assists
df_pe.to_csv('dash_groupedplayers_dataframe.csv')