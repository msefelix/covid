import os
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from datetime import date
from cofli.utils import load_pyfile
from cofli.settings import locations, bucket
from cofli.visual.cf_update_covidlive import fig_types
from cofli.visual.cf_update_vic import create_ts_figs

################## Todo
# Adjust repo for gcp & cf: # Update vic postcode data
# Add high level data preparation to cloud func

# Make app work on GCP

# Dep on app engine

# use bar chart & line chart combination for ts (not urgent)


################## Data loading
### Local mode
# fs = ''
# bucket = "/home/felix/learning/covid_aus"
### GCP mode
import gcsfs
fs = gcsfs.GCSFileSystem()

today = str(date.today())
year, month, day = map(int, today.split('-'))

covidlive_ts_figs = {location : {f"ts-figure-{fig_type}" : load_pyfile(f"{bucket}/data/covidlive/ts_figs/{location}_{fig_type}.pickle", fs=fs)
                                for fig_type in fig_types.keys()} 
                    for location in locations}

vic_gov_ts = pd.read_parquet(f"{bucket}/data/vic/cases_post.parquet")
vic_postcode_fig = load_pyfile(f"{bucket}/data/vic/vic_post_active_map.pickle", fs=fs)


################## App settings
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}


app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootswatch@5.1.3/dist/minty/bootstrap.min.css"],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )


################## App content building
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
    fig.layout.template = 'plotly_white'
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


def build_ts_tab():
    return  [
            html.Br(),
            dbc.Row(
                [
                dbc.Col(html.H5("Select location", className='text-center text-primary mb-4'), width=3),
                dbc.Col(html.H5("Select date range", className='text-center text-primary mb-4'), width=3)
                ],
                justify="evenly",
            ),
            dbc.Row(
                [
                dbc.Col(build_location_dropdown(), width=3), 
                dbc.Col(build_date_range(), width=3)
                ],
                justify="evenly",
            ),
            html.Br(),
            html.Div(id='covidlive-ts-plots')           
            ]


@app.callback(
    Output('vic-postcode-clicked', 'children'),
    Output('vic-postcode-ts', 'children'),
    Input('vic-postcode', 'clickData'))
def build_vic_postcode_ts(input_data):
    try:
        postcode = int(input_data['points'][0]['location'])
    except:
        postcode = 3000
    
    figs = create_ts_figs(vic_gov_ts, postcode)
    return f"Trend of Postcode {postcode}", [dbc.Col(dcc.Graph(id=f'vic-postcode-ts-{x}', figure=figs[x]), width=4) 
            for x in ['new', 'active pop %', 'approximate infected pop %']]

################## App layout
app.layout = dbc.Container([
                            html.H1("COVID-19 Trend in Australia", className='text-center text-primary mb-4'),
                            dcc.Tabs(id="top-tabs", value='timeseries', 
                                    children=[
                                            dcc.Tab(label='Evolution by state',
                                                    value='timeseries', 
                                                    children=build_ts_tab(),
                                                    style=tab_style, selected_style=tab_selected_style),
                                            dcc.Tab(label='Victoria by postcode',
                                                    value='vic-postcode',
                                                    children=[
                                                            html.H5("""Click an area on map to view details. Color reflects the percentage of active cases out of the population.
                                                                       *Caveat*: Population data is not up-to-date and it will be updated with census 2021 data once available""",
                                                                    className='text-center text-primary mb-4'),
                                                            dbc.Row(dcc.Graph(id='vic-postcode', figure=vic_postcode_fig)),
                                                            html.Br(),
                                                            html.H4(id='vic-postcode-clicked', className='text-center text-primary mb-4'),
                                                            dbc.Row(id='vic-postcode-ts')
                                                            ],
                                                    style=tab_style, selected_style=tab_selected_style)
                                    ], style=tabs_styles)
                            ])


if __name__ == '__main__':
    debug = False if os.environ["DASH_DEBUG_MODE"] == "False" else True
    app.run_server(port=8080, debug=debug)


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