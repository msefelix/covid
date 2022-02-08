import pickle


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