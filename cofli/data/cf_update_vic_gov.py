import requests
import gcsfs
import pandas as pd
from cofli.settings import folder, today


def fetch_url_to_gcs(fs, url: str, opath: str):
    """Download a file from the URL and save it at opath on GCS.

    Args:
        url (str): [description]
        opath (str): [description]
    """    
    response = requests.get(url)
    with fs.open(opath, 'wb') as f:
        f.write(response.content)
    return


def vic_by_location():
    fs = gcsfs.GCSFileSystem()
    
    vic_active_by_gov = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9oKYNQhJ6v85dQ9qsybfMfc-eaJ9oKVDZKx-VGUr6szNoTbvsLTzpEaJ3oW_LZTklZbz70hDBUt-d/pub?gid=0&single=true&output=csv"
    fetch_url_to_gcs(fs, vic_active_by_gov, f"{folder}/vic_active_by_gov_{today}.csv")

    vic_active_by_post = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwXSqlP56q78lZKxc092o6UuIyi7VqOIQj6RM4QmlVPgtJZfbgzv0a3X7wQQkhNu8MFolhVwMy4VnF/pub?gid=0&single=true&output=csv"
    fetch_url_to_gcs(fs, vic_active_by_post, f"{folder}/vic_active_by_post_{today}.csv")

    return


def process_a_post(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates().dropna(subset=['postcode'])
    df['postcode'] = df['postcode'].fillna(9999).astype(int)
    df['population'] = df['population'].fillna(0)

    cols = ['postcode', 'population', 'active', 'cases', 'new', 'data_date', 'file_processed_date']
    df = df[cols]

    df['data_date'] = pd.to_datetime(df['data_date'], format="%d/%m/%Y")
    df['file_processed_date'] = pd.to_datetime(df['file_processed_date'], format="%Y-%m-%d")

    df['active pop %'] = (df['active'] / df['population'] * 100).round(2)
    df['approximate infected pop %'] = (df['cases'] / df['population'] * 100).round(2)

    return df


def add_a_csv(filename='post'):
    df_new = pd.read_csv(f"{folder}/vic_active_by_{filename}_{today}.csv")
    df_new = process_a_post(df_new)

    df_old = pd.read_parquet(f"{folder}/data/vic/cases_{filename}.parquet")

    df = pd.concat([df_old, df_new], axis=0, ignore_index=True).drop_duplicates()
    df.to_parquet(f"{folder}/data/vic/cases_{filename}.parquet")
    return