import pickle
import gcsfs
import plotly.express as px


def load_fig(ipath):
    fs = gcsfs.GCSFileSystem()
    with fs.open(ipath, "rb") as f:
        fig = pickle.load(f)
    return fig


def save_fig(fig, opath):
    fs = gcsfs.GCSFileSystem()
    with fs.open(opath, "wb") as f:
        pickle.dump(fig, f)
    return


def make_a_ts_fig(df, x, y):
    fig = px.line(df, x=x, y=y, title=y)
    fig.update_traces(mode='lines+markers')
    return fig