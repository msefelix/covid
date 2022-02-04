import dash
from dash import html
from dash import dcc
from cofli.visual.utils import load_fig
from cofli.settings import locations
from cofli.visual.cf_update_covidlive import fig_types


folder = "/home/felix/learning/covid_aus"
covidlive_ts_figs = {location : {fig_type : load_fig(f"{folder}/data/covidlive/ts_figs/{location}_{fig_type}.pickle")
                                for fig_type in fig_types.keys()} 
                    for location in locations}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.renderer = 'var renderer = new DashRenderer();'

def _build_ts_graph(id, figures, cname):
    return dcc.Graph(id=id, figure=figures[id], className=cname)

def build_ts_by_location(covidlive_ts_figs, location):
    figures = covidlive_ts_figs[location]
    return html.Div([html.Div([
                                _build_ts_graph('active (k)', figures, 'six columns'),
                                _build_ts_graph('hosp', figures, 'six columns')
                            ],
                            className='three rows'),
                    html.Div([
                                _build_ts_graph('new', figures, 'six columns'),
                                _build_ts_graph('deaths', figures, 'six columns'),
                            ],
                            className='three rows'),
                    html.Div([
                                _build_ts_graph('icu', figures, 'six columns'),
                                _build_ts_graph('vent', figures, 'six columns'),
                            ],
                            className='three rows')
                    ],
                    className='nine rows')


app.layout = html.Div([build_ts_by_location(covidlive_ts_figs, 'vic')])


if __name__ == '__main__':
    app.run_server(debug=True)