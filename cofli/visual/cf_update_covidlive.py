import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from cofli.settings import locations
from cofli.visual.utils import save_fig
fig_types = {'new':'Daily New Cases (PCR + RAT)',
                                    'deaths':'Daily Lives Lost',
                                    'hosp':'Currently Hospitalised', 
                                    'icu':'Currently in ICU', 
                                    'vent':'Currently On Ventilator', 
                                    'active (k)':'Active Cases in Thousands', 
                                    'tests (k)':'Daily PCR Test in Thousands'}


def make_a_ts_fig(df: pd.DataFrame, y:str, title:str):
    cols = ['DAILY', '7D AVG']
    df_temp = df[[y, f"7D AVG - {y}"]]
    df_temp.columns = cols
    fig = px.line(df_temp, x=df_temp.index, y=cols, 
                  title=title, labels={'y':''})
    fig.update_layout(title={'y':0.99, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                    yaxis={'title':''}, 
                    xaxis={'title':''},
                    margin=go.layout.Margin(l=0, r=10, b=0, t=25),
                    legend=dict(yanchor='top', y=0.95, xanchor='left', x=0.05, title='')
                    )
    return fig


def make_ts_figs(rf: str):
    all_ts = {location : pd.read_parquet(f"{rf}/data/covidlive/{location}.parquet") for location in locations}

    for location in locations:
        for data_type, data_name in fig_types.items():
            fig = make_a_ts_fig(all_ts[location], data_type, data_name)
            save_fig(fig, f"{rf}/data/covidlive/ts_figs/{location}_{data_type}.pickle")

    return