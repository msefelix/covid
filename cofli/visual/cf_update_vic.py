import pandas as pd
import geopandas as gpd
import plotly.express as px
from cofli.settings import bucket, today
from cofli.visual.utils import save_fig
folder = f"{bucket}/data/vic/gov"


def update_figs(filename='post'):
    df = pd.read_parquet(f"{folder}/result/cases_{filename}.parquet")

    ### Update geo fig
    df_today = df.query(f"file_processed_date == '{today}'").set_index('postcode')

    gdf = gpd.read_file(f"{folder}/data/geo/vic/postcode.shp").set_index('postcode')
    df_today = gdf.join(df_today, how='right')

    fig = px.choropleth_mapbox(df_today,
                   locations=df_today.index,
                   geojson=df_today.geometry,
                   color="active pop %",
                   color_continuous_scale="Viridis",
                   range_color=(0, 4), #int(df['active pop %'].quantile(0.99)) + 1),
                   hover_data=['population', 'active', 'cases', 'new', 'active pop %', 'approximate infected pop %'],
                   mapbox_style="carto-positron",
                   center = {"lat": -37.8136, "lon": 144.9631}, # this is melbourne's lat long
                   opacity=0.5)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    save_fig(fig, f"{folder}/result/vic_post_active_map.pickle")

    ### Update VIC timeseries
    

    return