# Second plot, displaying the number of goals/assists/contributions for each
# player.
# Tick Buttons: Goal Assists
# Country Dropdown
# League Dropdown
# Position Dropdown

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'FUT Dashboard'

df = pd.read_pickle('data/fifa20_dash.pkl')

countries = [dict(label=str(c), value=str(c)) for c in df.nationality.unique()]
leagues = [dict(label=str(l), value=str(l)) for l in df.league.unique()]
positions = [dict(label=str(p), value=str(p)) for p in df.position.unique()]


# Define the application layout
app.layout = html.Div([

    # Title
    html.Div([
        html.H1(
            'FUT Dashboard',
            className= 'eight columns',
            style={'text-align': 'left'}
            ),
    ], className='row'
    ),

    # Separator
    html.Hr(style={'margin': '0', 'margin-bottom': '5'}),

    # Drop Downs
    html.Div([

        # Left most 
        html.Div([
            html.Label('Select a specific country:'),
            dcc.Dropdown(
                id='country',
                options=countries,
                value=None)],
            className = 'three columns'),

        # left 
        html.Div([
            html.Label('Select a specific league:'),
            dcc.Dropdown(
                id='league',
                options=leagues,
                value=None)],
            className= 'three columns'),

        # right
        html.Div([
            html.Label('Select a specific position:'),
            dcc.Dropdown(
                id='position',
                options=positions,
                value='ST')],
            className= 'three columns'),

        # right most 
        html.Div([
            html.Label('Contribution Type:'),
            dcc.RadioItems(
                id='contribution',
                options = [{'label': i, 'value': i} for i in ['Goals', 'Assists', 'Both']],
                value='Both',
                labelStyle={'display': 'inline-block'})],
            className= 'two columns')

    ],
    className='row',
    style={'margin-bottom': '20'}
    ),

    # rating slider
    html.Div([
        html.P("Move this slider to narrow down or broaden the rating search:"),
        dcc.RangeSlider(
            id='ratings',
            min=75,
            max=99,
            step=1,
            value=[84, 88],
            marks={str(overall): str(overall) for overall in df['overall'].unique()})
        ],
    className='row',
    style={'margin-bottom': '40'}
    ),

    # Separator
    html.Hr(style={'margin': '0', 'margin-bottom': '5'}),


    # price slider
    html.Div([
        html.P("Move this slider to narrow down the prices:"),
        dcc.RangeSlider(
            id='prices',
            min=1,
            max=4.5,
            step=0.1,
            value=[2.3, 2.7],
            marks={'1': '10K', '2': '100K', '3': '1M', '4': '10M'})
        ],
    className='row',
    style={'margin-bottom': '80'}
    ),


    # # price slider
    # html.Div([
    #     html.P("Move this slider to narrow down the prices:"),
    #     dcc.RangeSlider(
    #         id='prices',
    #         min=1,
    #         max=4.5,
    #         step=0.1,
    #         value=[2.3, 2.7],
    #         marks={str(i): str(10**i) + 'K' for i in range(1,5)})
    #     ],
    # className='row',
    # style={'margin-bottom': '80'}
    # ),


    dcc.Graph(id='graph-with-dropdowns'),
],

style = {
    'width': '85%',
    'max-width': '2000',
    'margin-left': 'auto',
    'margin-right': 'auto',
    'background-color': '#F3F3F3',
    'padding': '40',
    'padding-top': '20',
    'padding-bottom': '20',
}

)


@app.callback(
    Output('graph-with-dropdowns', 'figure'),
    [Input('country', 'value'),
     Input('league', 'value'),
     Input('position', 'value'),
     Input('contribution', 'value'),
     Input('ratings', 'value'),
     Input('prices', 'value')])

def update_graph(country, league, position, contribution, ratings, prices):
    df_ = df[(df.overall >= ratings[0]) & (df.overall <= ratings[1])]
    df_ = df_[(df_.price >= 1000*(10**prices[0])) & (df_.price <= 1000*(10**prices[1]))]
    if country != None:
        df_ = df_[df_.nationality == country]
    if league != None:
        df_ = df_[df_.league == league]
    if position != None:
        df_ = df_[df_.position == position]
    if contribution == 'Both':
        x = 'avg_contributions'
        x_t = 'Average Number of Contributions per Game'
    elif contribution == 'Goals':
        x = 'avg_goals'
        x_t = 'Average Number of Goals per Game'
    else:
        x = 'avg_assists'
        x_t = 'Average Number of Assists per Game'
    
    
    data =[]
    for res_id in df_.resource_id.unique():
        player_d = df_[df_.resource_id == res_id]
        data.append(go.Scatter(x=player_d[x],
                               y=player_d['price'],
                               mode='markers',
                               name=str(player_d.player_name.values[0]) + ' '+ str(player_d.overall.values[0]),
                               marker={
                                   'size': 10,
                                   'opacity': 0.5,
                                   'line': {'width': 0.5, 'color': 'blue'}
                               }
                    ))
        
    return {
        'data': data,
        'layout': go.Layout(
            xaxis={
                'title': x_t,
                'type': 'linear'
            },
            yaxis={
                'title': 'Price',
                'type': 'linear'
            },
            margin={'l': 40, 'b': 80, 't': 80, 'r': 40},
            hovermode='closest')
    }

if __name__ == '__main__':
    app.run_server(debug=True)