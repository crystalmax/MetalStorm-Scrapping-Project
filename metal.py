
import pandas as pd
import numpy as np
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

mapbox_access_token = 'pk.eyJ1IjoiY3J5c3RhbG0iLCJhIjoiY2p3cGJ1ZWF3MHZ2MjQwcHJ6ZjdtaHBtZCJ9.ylD2luL9p8CAHg0oZWrReg'
band = pd.read_csv('band.csv',index_col=0)
coordinates = pd.read_csv('coordinate.csv',index_col=0)
genre = band['Genre'].value_counts()
color = {'Black Metal':'Grey','Death Metal':'Red','Thrash Metal':'Blue','Doom Metal':'Purple','Heavy Metal':'Yellow'}
    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Until The Light Takes Us',style={
                                'textAlign': 'center',
                                'color':'#7f7f7f'}
           ),
    
    html.Div(children='A Century\'s Reign In Chaos', 
             style={
                    'textAlign': 'center'
                    }
            ),
    
    dcc.Dropdown(
        id='genre_select',
        options=[{'label': i, 'value': i} for i in ['Black Metal', 'Death Metal', 'Doom Metal',
       'Thrash Metal', 'Heavy Metal']],
        value=['Black Metal'],
        multi=True
    ),
    
    dcc.Dropdown(
        id='year_select',
        options=[{'label': i, 'value': i} for i in [1985,1990, 1995, 2000]],
        value=1995
    ),
    
    html.Div(
            '3510 Bands Info In Total', id='total-bands', style={'textAlign': 'center'}
    ),
    

    html.Div(               
            dcc.Graph(id='total_bands_genre',
                     figure={'data':[
                                     {'x':genre.index, 
                                      'y':genre.values,
                                      'type':'bar',
                                      'color':'Purple',
                                      'opacity':0.6
                                     }],
                            'layout':go.Layout(
                                        title='Genre',
                                        yaxis={'title':'Band Counts'},
                                        hovermode='closest'
                                        )
                            }
                
            )
    ),
    
    html.Div([dcc.Graph(id='origin_country',
                        className='six columns'),
              dcc.Graph(id='origin_year',
                        className='six columns'),
             ],className='Row'
            ),

    html.Div([
        html.Div([
                dcc.Graph(id='pop_year')
        ],
        className='six columns'),
        html.Div([
                dash_table.DataTable(id='score_table',
                                    columns=[
                                        {"name": i, "id": i} for i in (band.reset_index().rename(columns={'index':'Band'}).columns)
                                    ],
                                    sort_action='native',
                                    filter_action='native'
                                    )]
            ,className='six columns')                
        ],className='Row')
    ])


@app.callback(
    dash.dependencies.Output('origin_country', 'figure'),
    [dash.dependencies.Input('genre_select', 'value')])
def update_country_graph(genres):
    traces = []
    for genre in genres:
        traces.append(go.Scattermapbox(
                        lat=coordinates[coordinates['Genre']==f'{genre}']['Lat'],
                        lon=coordinates[coordinates['Genre']==f'{genre}']['Long'],
                        mode='markers',
                        marker = {
                                'size': coordinates[coordinates['Genre']==f'{genre}']['Bands']/2,
                                'sizemode': 'diameter',
                                'color': color[f'{genre}'],
                                'opacity': 0.6
                        },
                        text = list(zip(coordinates[coordinates['Genre']==f'{genre}'].index,
                                        coordinates[coordinates['Genre']==f'{genre}']['Bands'])),
                        name = f'{genre}'
                        )
                    )
    return {
            'data': traces,
                     
            'layout':go.Layout(
                        title='Origin Map',
                        autosize=True,
                        hovermode='closest',
                        mapbox=dict(
                                accesstoken=mapbox_access_token,
                                bearing=0,
                                center=dict(
                                        lat=45.7465,
                                        lon=-39.4629
                                        ),
                        pitch=0,
                        zoom=1
                        ),
            )
    }


@app.callback(
    dash.dependencies.Output('origin_year', 'figure'),
    [dash.dependencies.Input('genre_select', 'value')])
def update_year_graph(genres):
    traces = []
    for genre in genres:
        traces.append(go.Line(
                        x=band[band['Genre']==f'{genre}']['Formed'].value_counts().sort_index().index, 
                        y=band[band['Genre']==f'{genre}']['Formed'].value_counts().sort_index().values,
                        text=band[band['Genre']==f'{genre}']['Formed'].value_counts().sort_index().index,
                        textposition='top center',
                        name = f'{genre}'
                        )
        )
    return {
            'data': traces,
        
            'layout': go.Layout(
                        title='Bands Formed By Year',
                        xaxis=dict(title='Year',
                                  tickangle=45,
                                  tickfont=dict(family='Rockwell',
                                                size=15
                                            )
                                  ),
                        yaxis=dict(title='Band Counts')
                    )
            }

@app.callback(
    dash.dependencies.Output('pop_year', 'figure'),
    [dash.dependencies.Input('genre_select', 'value'),
     dash.dependencies.Input('year_select', 'value')])
def update_pop_graph(genre_select,year_select):
    pop = band[(band['Formed']==year_select)&(band['Genre'].isin(genre_select))].groupby('Genre').agg({'Genre':'count'})

    return {
            'data': [go.Pie(labels=pop.index,
                           values=pop['Genre'],
                           hoverinfo='label+percent',
                           text=pop['Genre']
                    )],
            'layout':go.Layout(
                            title=f'Popularity in {year_select}',     
                            hovermode='closest'
            )
    }

@app.callback(
    dash.dependencies.Output('score_table', 'data'),
    [dash.dependencies.Input('genre_select', 'value')])
def update_table(genre_select):
    table = []
    for genre in genre_select:
        table.append(band[(band['Genre']==f'{genre}')].sort_values(by='Avg_Score',ascending=False)
                     .head(5).reset_index().rename(columns={'index':'Band'})
        )

    return pd.concat(table).to_dict('records') if table != [] else []


if __name__ == '__main__':
    app.run_server(debug=True)
