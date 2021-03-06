import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from datetime import date
from cofli.visual.cf_update_covidlive import make_all_ts_figs
import pandas as pd
import plotly.graph_objects as go

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

# Trial with log
import logging
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


def build_date_range(year, month, day, today, date_2m_ago):
    return  dcc.DatePickerRange(
        id='ts-date-picker',
        min_date_allowed=date(2020, 1, 26),
        max_date_allowed=date(year, month, day),
        start_date=date_2m_ago,
        end_date=today,
        style={'align-items': 'center', 'justify-content': 'center'})


def _build_ts_graph(id, figures, start_date, end_date):
    # Load figure data as json
    fig = figures[id.split("-")[-1]]

    # Recreate plolty figure and adjust the x axis range
    fig = go.Figure(fig)
    fig.update_xaxes(range=[start_date, end_date])

    # Compute the max value of y within the given x range and adjust the y axis range
    x = fig['data'][0]['x']
    y = fig['data'][0]['y']
    xy = pd.Series(index=x, data=y)
    y_max = xy.loc[start_date : end_date].max()
    fig.update_yaxes(range=[0, y_max + max(1, int(y_max * 0.05))])

    return dcc.Graph(id=id, figure=fig)


def build_ts_tab(year, month, day, today, date_2m_ago):
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
                dbc.Col(build_date_range(year, month, day, today, date_2m_ago), width=3)
                ],
                justify="evenly",
            ),
            html.Br()  
            ]


@app.callback(
    Output(component_id='covidlive-ts-plots', component_property='children'),
    Input(component_id='my-store', component_property='data'),
    Input(component_id='location-dropdown', component_property='value'),
    Input('ts-date-picker', 'start_date'),
    Input('ts-date-picker', 'end_date')
)
def build_ts_by_location(my_store, location, start_date, end_date):
    figures = my_store['covidlive-figs'][location]
    return html.Div([
                    dbc.Row([
                                dbc.Col(_build_ts_graph('ts-figure-active', figures, start_date, end_date), width=6),
                                dbc.Col(_build_ts_graph('ts-figure-hosp', figures, start_date, end_date), width=6)
                            ]),
                    dbc.Row([
                                dbc.Col(_build_ts_graph('ts-figure-new', figures, start_date, end_date), width=6),
                                dbc.Col(_build_ts_graph('ts-figure-deaths', figures, start_date, end_date), width=6)
                            ]),
                    dbc.Row([
                                dbc.Col(_build_ts_graph('ts-figure-icu', figures, start_date, end_date), width=6),
                                dbc.Col(_build_ts_graph('ts-figure-vent', figures, start_date, end_date), width=6)
                            ]),
                    ]
                    )

################## App layout
# TODO: Use client side callback
def serve_layout():
    # Load covidlive data and make plolty figures, which will be stored on the client side.
    all_ts = pd.read_parquet(f"./data/covidlive/all.parquet")
    today = str(all_ts.index.max()).split(" ")[0]
    year, month, day = map(int, today.split("-"))
    covidlive_figures = make_all_ts_figs(all_ts)

    # By default, set the date range between today and two months ago
    date_2m_ago = str((pd.Timestamp(today) - pd.DateOffset(months=2)).date())

    # Prepare layout
    layout = html.Div([
                        dcc.Store(id='my-store', data={'covidlive-figs': covidlive_figures}),
                        dbc.Container([    
                            html.H1("COVID-19 Trend in Australia (raw and 7-Day average)", className='text-center text-primary mb-4'),
                            html.H3("Data Source: https://covidlive.com.au/", className='text-center text-primary mb-4'),
                            dcc.Tabs(id="top-tabs", value='timeseries', 
                                    children=[
                                            dcc.Tab(label='Please select location and date range',
                                                    value='timeseries', 
                                                    children=build_ts_tab(year, month, day, today, date_2m_ago) + [html.Div(id='covidlive-ts-plots')],
                                                    style=tab_style, selected_style=tab_selected_style),
                                        ], style=tabs_styles)
                                ])])
    
    return layout


app.layout = serve_layout
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)