import gcsfs
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from cofli.settings import locations, bucket
from cofli.utils import save_pyfile
fig_types = {'new':'Daily New Cases (PCR + RAT)',
                                    'deaths':'Daily Lives Lost',
                                    'hosp':'Hospitalised', 
                                    'icu':'In ICU', 
                                    'vent':'On Ventilator', 
                                    'active':'Active Cases', 
                                    'tests':'PCR Test'}


def make_a_ts_fig(df: pd.DataFrame, y:str, title:str):
    cols = ['RAW', '7D AVG']
    df_temp = df[[y, f"7D AVG - {y}"]]
    df_temp.columns = cols
    fig = px.line(df_temp, x=df_temp.index, y=cols, 
                  title=title, labels={'y':''}, height=350)
    fig.update_layout(title={'y':0.99, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                    yaxis={'title':''}, 
                    xaxis={'title':''},
                    margin=go.layout.Margin(l=0, r=10, b=20, t=25),
                    showlegend=False # legend=dict(yanchor='top', y=0.95, xanchor='left', x=0.05, title='')
                    )
    return fig


def make_ts_figs(root_folder=bucket):
    all_figs = {}
    all_ts = pd.read_parquet(f"{root_folder}/data/covidlive/all.parquet")

    for location in locations:
        df = all_ts.query(f"location == '{location}'")
        figs = {}
        for data_type, data_name in fig_types.items():
            fig = make_a_ts_fig(df, data_type, data_name)
            figs[data_type] = fig
     
        all_figs[location] = figs

    return all_figs