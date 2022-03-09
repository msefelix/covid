import logging
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from datetime import date
from cofli.visual.cf_update_covidlive import make_ts_figs

################## Settings for main, app.yaml and Dockerfile
# https://towardsdatascience.com/dockerize-your-dash-app-1e155dd1cea3


################## Todo
# Make y-axis range auto adjustable when changing x-axis (date range)
# Predictions
# Lookup by postcode
# Email stats to registered user


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

# Expose Flask instance
server = app.server

# Trial with logging
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(logging.DEBUG)


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


def build_date_range(today, year, month, day):
    return  dcc.DatePickerRange(
        id='ts-date-picker',
        min_date_allowed=date(2020, 1, 26),
        max_date_allowed=date(year, month, day),
        start_date='2021-12-01',
        end_date=today,
        style={'align-items': 'center', 'justify-content': 'center'})


def _build_ts_graph(id, figures, date_ranges):
    fig = figures[id.split("-")[-1]]
    fig = fig.update_xaxes(range=date_ranges)
    fig = fig.update_yaxes(autorange=True, fixedrange=False)
    fig.layout.template = 'plotly_white'
    return dcc.Graph(id=id, figure=fig)


@app.callback(Output('covidlive-ts-cache', 'data'),
Input(component_id='trigger', component_property='value'))
def load_covidlive():
     return make_ts_figs(".")


@app.callback(
    Output(component_id='covidlive-ts-plots', component_property='children'),
    Input(component_id='covidlive-ts-cache', component_property='data'),
    Input(component_id='location-dropdown', component_property='value'),
    Input('ts-date-picker', 'start_date'),
    Input('ts-date-picker', 'end_date')
)
def build_ts_by_location(covidlive_ts_cache, location, start_date, end_date):
# FIXME Decouple figure update induced by date from location induced update
    figures = covidlive_ts_cache[0][location]
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

@app.callback(
    Output(component_id='covidlive-ts-tab', component_property='children'),
    Input(component_id='covidlive-ts-cache', component_property='data'))
def build_ts_tab(covidlive_ts_cache):
    today = covidlive_ts_cache[1]
    year, month, day = map(int, today.split("-"))
    return  [
            html.Br(),
            dbc.Row(
                [
                dbc.Col(html.H5("Location", className='text-center text-primary mb-4'), width=3),
                dbc.Col(html.H5("Date range", className='text-center text-primary mb-4'), width=3)
                ],
                justify="evenly",
            ),
            dbc.Row(
                [
                dbc.Col(build_location_dropdown(), width=3), 
                dbc.Col(build_date_range(today, year, month, day), width=3)
                ],
                justify="evenly",
            ),
            html.Br()          
            ]

################## App layout
def get_layout():
    
    layout = dbc.Container([html.H1("hello", id="trigger"),
                            html.Div(id="covidlive-ts-cache"),
                            html.H1("COVID-19 Trend in Australia (raw and 7-Day average)", className='text-center text-primary mb-4'),
                            html.H3("Data Source: https://covidlive.com.au/", className='text-center text-primary mb-4'),
                            dcc.Tabs(id="top-tabs", value='timeseries', 
                                    children=[dcc.Store(id='intermediate-value'),
                                            dcc.Tab(label='Please select location and date range',
                                                    value='timeseries', 
                                                    children=[html.Div(id='covidlive-ts-tab'),
                                                              html.Div(id='covidlive-ts-plots')],
                                                    style=tab_style, selected_style=tab_selected_style),
                                    ], style=tabs_styles)
                            ])
    return layout


app.layout = get_layout()

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8080)