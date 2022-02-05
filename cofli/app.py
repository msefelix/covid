import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
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


@app.callback(
    Output(component_id='covidlive-ts-plots', component_property='children'),
    Input(component_id='location-dropdown', component_property='value')
)
def build_ts_by_location(location):
    figures = covidlive_ts_figs[location]
    return html.Div([html.Div([
                                _build_ts_graph('active (k)', figures, 'six columns'),
                                _build_ts_graph('hosp', figures, 'six columns')
                            ],
                            className='two rows'),
                    html.Div([
                                _build_ts_graph('new', figures, 'six columns'),
                                _build_ts_graph('deaths', figures, 'six columns'),
                            ],
                            className='two rows'),
                    html.Div([
                                _build_ts_graph('icu', figures, 'six columns'),
                                _build_ts_graph('vent', figures, 'six columns'),
                            ],
                            className='two rows')
                    ],
                    className='six rows'
                    )


def build_location_dropdown():
    return dcc.Dropdown(
        id='location-dropdown',
        options=[
            {'label': 'Australia', 'value': 'aus'},
            {'label': 'Victoria', 'value': 'vic'},
            {'label': 'New South Wales', 'value': 'nsw'}
        ],
        value='aus', className='twelve rows'
    )


app.layout = html.Div([build_location_dropdown(),
                      html.Div(id='covidlive-ts-plots')])


if __name__ == '__main__':
    app.run_server(debug=True)