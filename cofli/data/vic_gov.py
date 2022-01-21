import requests
import gcsfs
from datetime import date
folder = "gs://covid-analytics-data/data/vic/gov"
today = str(date.today())


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


def vic_by_location(event, context):
    fs = gcsfs.GCSFileSystem()
    
    vic_active_by_gov = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9oKYNQhJ6v85dQ9qsybfMfc-eaJ9oKVDZKx-VGUr6szNoTbvsLTzpEaJ3oW_LZTklZbz70hDBUt-d/pub?gid=0&single=true&output=csv"
    fetch_url_to_gcs(fs, vic_active_by_gov, f"{folder}/vic_active_by_gov_{today}.csv")

    vic_active_by_post = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwXSqlP56q78lZKxc092o6UuIyi7VqOIQj6RM4QmlVPgtJZfbgzv0a3X7wQQkhNu8MFolhVwMy4VnF/pub?gid=0&single=true&output=csv"
    fetch_url_to_gcs(fs, vic_active_by_post, f"{folder}/vic_active_by_post_{today}.csv")

    return