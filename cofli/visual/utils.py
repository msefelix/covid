import pickle
import gcsfs


def load_fig(ipath, fs=''):
    if fs == '':
        with open(ipath, "rb") as f:
            fig = pickle.load(f)
    else:
        fs = gcsfs.GCSFileSystem()
        with fs.open(ipath, "rb") as f:
            fig = pickle.load(f)
    return fig


def save_fig(fig, opath, fs=''):
    if fs == '':
        with open(opath, "wb") as f:
            pickle.dump(fig, f)
    else:
        fs = gcsfs.GCSFileSystem()
        with fs.open(opath, "wb") as f:
            pickle.dump(fig, f)
    return