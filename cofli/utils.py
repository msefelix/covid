import pickle
import tempfile
import zipfile
import gcsfs
import geopandas as gpd


def load_pyfile(ipath, fs=''):
    if fs == '':
        with open(ipath, "rb") as f:
            pyfile = pickle.load(f)
    else:
        with fs.open(ipath, "rb") as f:
            pyfile = pickle.load(f)
    return pyfile


def save_pyfile(pyfile, opath, fs=''):
    if fs == '':
        with open(opath, "wb") as f:
            pickle.dump(pyfile, f)
    else:
        with fs.open(opath, "wb") as f:
            pickle.dump(pyfile, f)
    return


def read_gcs_zip(path: str, **kwargs):
    fs = gcsfs.GCSFileSystem()
    with tempfile.TemporaryDirectory() as d:
        with fs.open(path, "rb") as f:
            zipf = zipfile.ZipFile(f, "r")
            zipf.extractall(d)

            for name in zipf.namelist():
                if name.endswith("/"):
                    d += "/" + name
                    break
        return gpd.read_file(d, **kwargs)