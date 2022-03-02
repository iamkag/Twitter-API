import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import search_tweets

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server = app.server
app.server.config[
    "SQLALCHEMY_DATABASE_URI"] = "postgres://<YOUR-CREDENTIALS>"
sidebar = html.Div(
    [
        html.H5("Twitter API", className="display-4"),
        html.Hr(),
        html.P(
            "Query Search", className='lead'
        ),
        dcc.Input(id='query', type='text', placeholder='e.g. Mykonos, Santorini', debounce=True),
        html.P("In which year", className='lead'),
        dcc.Input(id='year', type='number', debounce=True, max=2022, min=2016, step=1),
        html.Hr(),
        html.Button('Generate Graphs', id='button'),
    ],
    style=SIDEBAR_STYLE,
)
main_app = html.Div([

    dcc.Loading(id='loading-world-fig', type='default',
                children=dcc.Graph(id='world_fig', style={'display': 'inline-block'})),
    dcc.Loading(id='loading-hist', type='default', children=dcc.Graph(id='hist', style={'display': 'inline-block'})),
    dcc.Loading(id='loading-line-plot', type='default',
                children=dcc.Graph(id='line-plot', style={'display': 'inline-block'}))
], style={'textAlign': 'center'})

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    main_app
])


@app.callback(
    Output(component_id='world_fig', component_property='figure'),
    Output(component_id='hist', component_property='figure'),
    Output(component_id='line-plot', component_property='figure'),
    Input(component_id='button', component_property='n_clicks'),
    State(component_id='year', component_property='value'),
    State(component_id='query', component_property='value'),
    prevent_initial_call=False
)
def update_figure(n_clicks, year, query):
    search_words = []
    for item in query.split(', '):
        search_words.append(item)
    world_fig, hist, line_plot = search_tweets.twitter_procedure(search_words, year)
  
    print("RUN")
    return world_fig, hist, line_plot


if __name__ == '__main__':
    app.run_server()
