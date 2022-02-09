import gcsfs
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from cofli.settings import bucket, today
from cofli.utils import save_pyfile, read_gcs_zip


def update_geo_fig(filename='post'):
    df = pd.read_parquet(f"{bucket}/data/vic/cases_{filename}.parquet")
    df_today = df.query(f"file_processed_date == '{today}'").set_index('postcode')
    gdf = read_gcs_zip(f"{bucket}/data/geo/vic/vic.zip").set_index('postcode')
    df_today = gdf.join(df_today, how='right')

    fig = px.choropleth_mapbox(df_today,
                   locations=df_today.index,
                   geojson=df_today.geometry,
                   color="active pop %",
                   color_continuous_scale="Viridis",
                   range_color=(0, round(df['active pop %'].quantile(0.8), 0)),
                   hover_data=['population', 'active', 'cases', 'new', 'active pop %', 'approximate infected pop %'],
                   mapbox_style="carto-positron",
                   center = {"lat": -37.8136, "lon": 144.9631}, # this is melbourne's lat long
                   opacity=0.5, height=600)
    fig.update_geos(fitbounds="locations", visible=False) # fs is instantiated here due to cloud function 'bug'
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    save_pyfile(fig, f"{bucket}/data/vic/vic_post_active_map.pickle", fs=gcsfs.GCSFileSystem())

    return


def make_a_ts_fig(df: pd.DataFrame, y:str, title: str=''):
    if title == '':
        title = y

    fig = px.line(df, x='date', y=y, 
                  title=title, labels={'y':''},
                  height=300)
    fig.update_layout(title={'y':0.99, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                    yaxis={'title':''}, 
                    xaxis={'title':''},
                    margin=go.layout.Margin(l=0, r=10, b=20, t=25),
                    showlegend=False)
    fig.layout.template = 'plotly_white'
    fig.update_traces(mode='lines+markers')
    return fig


def create_ts_figs(vic_gov_ts, postcode:int):
    df = vic_gov_ts.query(f"postcode == {postcode}").rename(columns={'data_date':'date'}).sort_values('date')
    return {col : make_a_ts_fig(df, col, title) for col, title in 
            {
            # 'active': '# of Active Cases', 
            # 'cases': '# of Total Cases',
            'new': '# of New Cases (PCR)',
            'active pop %': '% of Active Cases out of Population',
            'approximate infected pop %': '% of Total Cases out of Population'
            }.items()}