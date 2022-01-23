import pickle
import gcsfs
import pandas as pd
import geopandas as gpd
import plotly.express as px
from datetime import date
folder = "gs://covid-analytics-data/data/vic/gov"
today = str(date.today())


def load_fig(ipath):
    fs = gcsfs.GCSFileSystem()
    with fs.open(ipath, "rb") as f:
        fig = pickle.load(f)
    return fig