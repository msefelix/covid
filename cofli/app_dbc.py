import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from datetime import date
from cofli.visual.utils import load_fig
from cofli.settings import locations
from cofli.visual.cf_update_covidlive import fig_types


import dash_bootstrap_components as dbc
# https://www.bootstrapcdn.com/bootswatch/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )


folder = "/home/felix/learning/covid_aus"
today = str(date.today())
year, month, day = map(int, today.split('-'))


covidlive_ts_figs = {location : {f"ts-figure-{fig_type}" : load_fig(f"{folder}/data/covidlive/ts_figs/{location}_{fig_type}.pickle")
                                for fig_type in fig_types.keys()} 
                    for location in locations}


def build_location_dropdown():
    return dcc.Dropdown(
        id='location-dropdown',
        options=[
            {'label': 'Australia', 'value': 'aus'},
            {'label': 'ACT', 'value': 'act'},
            {'label': 'New South Wales', 'value': 'nsw'},
            {'label': 'North Territory', 'value': 'nt'},
            {'label': 'Queensland', 'value': 'qld'},
            {'label': 'South Australia', 'value': 'sa'},
            {'label': 'Tasmania', 'value': 'tas'},
            {'label': 'Victoria', 'value': 'vic'},
            {'label': 'West Australia', 'value': 'wa'}
        ],
        value='aus',
        style={'align-items': 'center', 'justify-content': 'center'}
    )


def build_date_range():
    return  dcc.DatePickerRange(
        id='ts-date-picker',
        min_date_allowed=date(2020, 1, 26),
        max_date_allowed=date(year, month, day),
        start_date='2021-12-01',
        end_date=today,
        style={'align-items': 'center', 'justify-content': 'center'})


def _build_ts_graph(id, figures, date_ranges):
    fig = figures[id]
    fig = fig.update_xaxes(range=date_ranges)
    return dcc.Graph(id=id, figure=fig)


@app.callback(
    Output(component_id='covidlive-ts-plots', component_property='children'),
    Input(component_id='location-dropdown', component_property='value'),
    Input('ts-date-picker', 'start_date'),
    Input('ts-date-picker', 'end_date')
)
def build_ts_by_location(location, start_date, end_date):
# FIXME Decouple figure update induced by date from location induced update
    figures = covidlive_ts_figs[location]
    date_ranges = (str(start_date), str(end_date))
    return html.Div([
                    dbc.Row([
                                dbc.Col(_build_ts_graph('ts-figure-active', figures, date_ranges), width=6),
                                dbc.Col(_build_ts_graph('ts-figure-hosp', figures, date_ranges), width=6)
                            ]),
                    dbc.Row([
                                dbc.Col(_build_ts_graph('ts-figure-new', figures, date_ranges), width=6),
                                dbc.Col(_build_ts_graph('ts-figure-deaths', figures, date_ranges), width=6)
                            ]),
                    dbc.Row([
                                dbc.Col(_build_ts_graph('ts-figure-icu', figures, date_ranges), width=6),
                                dbc.Col(_build_ts_graph('ts-figure-vent', figures, date_ranges), width=6)
                            ]),
                    ]
                    )


app.layout = dbc.Container([
            dbc.Row(
                [dbc.Col(html.H3("Select an area", className='text-center text-primary mb-4'), width=6),
                dbc.Col(html.H3("Select date range", className='text-center text-primary mb-4'), width=6)]
            ),
            dbc.Row(
                [dbc.Col(html.Div(), width=1),
                dbc.Col(build_location_dropdown(), width=4), 
                dbc.Col(html.Div(), width=3),
                dbc.Col(build_date_range(), width=4)]
            ),
            html.Div(id='covidlive-ts-plots')              
                            ])


if __name__ == '__main__':
    app.run_server(debug=True)


# # # Layout section: Bootstrap (https://hackerthemes.com/bootstrap-cheatsheet/)
# # # ************************************************************************
# app.layout = dbc.Container([

#     dbc.Row(
#         dbc.Col(html.H1("Stock Market Dashboard",
#                         className='text-center text-primary mb-4'),
#                 width=12)
#     ),

#     dbc.Row([

#         dbc.Col([
#             dcc.Dropdown(id='my-dpdn', multi=False, value='AMZN',
#                          options=[{'label':x, 'value':x}
#                                   for x in sorted(df['Symbols'].unique())],
#                          ),
#             dcc.Graph(id='line-fig', figure={})
#         ],# width={'size':5, 'offset':1, 'order':1},
#            xs=12, sm=12, md=12, lg=5, xl=5
#         ),

#         dbc.Col([
#             dcc.Dropdown(id='my-dpdn2', multi=True, value=['PFE','BNTX'],
#                          options=[{'label':x, 'value':x}
#                                   for x in sorted(df['Symbols'].unique())],
#                          ),
#             dcc.Graph(id='line-fig2', figure={})
#         ], #width={'size':5, 'offset':0, 'order':2},
#            xs=12, sm=12, md=12, lg=5, xl=5
#         ),

#     ], no_gutters=True, justify='start'),  # Horizontal:start,center,end,between,around

#     dbc.Row([
#         dbc.Col([
#             html.P("Select Company Stock:",
#                    style={"textDecoration": "underline"}),
#             dcc.Checklist(id='my-checklist', value=['FB', 'GOOGL', 'AMZN'],
#                           options=[{'label':x, 'value':x}
#                                    for x in sorted(df['Symbols'].unique())],
#                           labelClassName="mr-3"),
#             dcc.Graph(id='my-hist', figure={}),
#         ], #width={'size':5, 'offset':1},
#            xs=12, sm=12, md=12, lg=5, xl=5
#         ),

#         dbc.Col([
#             dbc.Card(
#                 [
#                     dbc.CardBody(
#                         html.P(
#                             "We're better together. Help each other out!",
#                             className="card-text")
#                     ),
#                     dbc.CardImg(
#                         src="https://media.giphy.com/media/Ll0jnPa6IS8eI/giphy.gif",
#                         bottom=True),
#                 ],
#                 style={"width": "24rem"},
#             )
#         ], #width={'size':5, 'offset':1},
#            xs=12, sm=12, md=12, lg=5, xl=5
#         )
#     ], align="center")  # Vertical: start, center, end

# ], fluid=True)


# # Callback section: connecting the components
# # ************************************************************************
# # Line chart - Single
# @app.callback(
#     Output('line-fig', 'figure'),
#     Input('my-dpdn', 'value')
# )
# def update_graph(stock_slctd):
#     dff = df[df['Symbols']==stock_slctd]
#     figln = px.line(dff, x='Date', y='High')
#     return figln


# # Line chart - multiple
# @app.callback(
#     Output('line-fig2', 'figure'),
#     Input('my-dpdn2', 'value')
# )
# def update_graph(stock_slctd):
#     dff = df[df['Symbols'].isin(stock_slctd)]
#     figln2 = px.line(dff, x='Date', y='Open', color='Symbols')
#     return figln2


# # Histogram
# @app.callback(
#     Output('my-hist', 'figure'),
#     Input('my-checklist', 'value')
# )
# def update_graph(stock_slctd):
#     dff = df[df['Symbols'].isin(stock_slctd)]
#     dff = dff[dff['Date']=='2020-12-03']
#     fighist = px.histogram(dff, x='Symbols', y='Close')
#     return fighist


# if __name__=='__main__':
#     app.run_server(debug=True, port=8000)

    
# # https://youtu.be/0mfIK8zxUds