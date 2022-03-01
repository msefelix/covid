from gcloud import storage
from pathlib import Path
from cofli.settings import bucket

bucket_obj = storage.Client().get_bucket(bucket.split("//")[1])

folder = "data/covidlive"
Path(folder).mkdir(parents=True, exist_ok=True)
blob = bucket_obj.blob(f"{folder}/all.parquet")
blob.download_to_filename(f"{folder}/all.parquet")