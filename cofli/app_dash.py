import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from datetime import date
from cofli.visual.utils import load_fig
from cofli.settings import locations
from cofli.visual.cf_update_covidlive import fig_types

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.renderer = 'var renderer = new DashRenderer();'


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
        className='four columns',
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


def _build_ts_graph(id, figures, cname, date_ranges):
    fig = figures[id]
    fig = fig.update_xaxes(range=date_ranges)
    return dcc.Graph(id=id, figure=fig, className=cname)


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
    return html.Div([html.Div([
                                _build_ts_graph('ts-figure-active', figures, 'six columns', date_ranges),
                                _build_ts_graph('ts-figure-hosp', figures, 'six columns', date_ranges)
                            ],
                            className='two rows'),
                    html.Div([
                                _build_ts_graph('ts-figure-new', figures, 'six columns', date_ranges),
                                _build_ts_graph('ts-figure-deaths', figures, 'six columns', date_ranges),
                            ],
                            className='two rows'),
                    html.Div([
                                _build_ts_graph('ts-figure-icu', figures, 'six columns', date_ranges),
                                _build_ts_graph('ts-figure-vent', figures, 'six columns', date_ranges),
                            ],
                            className='two rows')
                    ],
                    className='six rows'
                    )


app.layout = html.Div([
                        html.Div([html.Div([
                                    html.H6("Select an area", className='four columns', style={'textAlign': 'center'}),
                                    build_location_dropdown()
                                    ], 
                                className='six columns'),
                        html.Div([
                                    html.H6("Select date range", className='four columns', style={'textAlign': 'center'}),
                                    build_date_range()
                                    ], 
                                className='six columns')]),
                        html.Div(id='covidlive-ts-plots')])


if __name__ == '__main__':
    app.run_server(debug=True)