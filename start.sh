gsutil cp "$BUCKET/data/covidlive/all.parquet" "./data/covidlive/all.parquet"
gsutil cp "$BUCKET/data/vic/cases_post.parquet" "./data/vic/cases_post.parquet"
gsutil cp "$BUCKET/data/vic/vic_post_active_map.pickle" "./data/vic/vic_post_active_map.pickle"

gunicorn --bind "0.0.0.0":$PORT app:server -t 60 --graceful-timeout 60