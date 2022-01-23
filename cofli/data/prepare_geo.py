import pandas as pd
import geopandas as gpd
from datetime import date
folder = "gs://covid-analytics-data/data/vic/gov"
today = str(date.today())


def prepare_vic_post(df: pd.DataFrame):
    # Load Geo data for postcode from source1
    gdf1 = gpd.read_file(f"{folder}/data/geo/1270055003_poa_2016_aust_shape.zip")
    gdf1['POA_CODE16'] = gdf1['POA_CODE16'].astype(int)
    gdf1 = gdf1.query("POA_CODE16 >= 3000 and POA_CODE16 < 4000")

    # Load Geo data for postcode from source2
    gdf2 = gpd.read_file(f"{folder}/data/geo/VMADMIN")
    gdf2['POSTCODE'] = gdf2['POSTCODE'].astype(int)
    gdf2 = gdf2.query("POSTCODE >= 3000 and POSTCODE < 4000")

    # Check missing postcode
    print(set(df['postcode']) - set(gdf1['POA_CODE16']))
    print(set(df['postcode']) - set(gdf2['POSTCODE']))

    # Combine
    gdf1 = gdf1.rename(columns={'POA_CODE16':'postcode'})[['postcode', 'geometry']]
    gdf2 = gdf2.query("POSTCODE == 3336").rename(columns={'POSTCODE':'postcode'})[['postcode', 'geometry']]
    gdf = pd.concat([gdf1, gdf2], axis=0, ignore_index=True)
    print(set(df['postcode']) - set(gdf2['POSTCODE']))
    print(set(gdf['postcode']) - set(df['postcode']))

    # Save
    gdf.to_file(f"{folder}/data/geo/vic/postcode.shp")

    return