FROM python:3.7

ENV FSTYPE="gcs" BUCKET="gcs://covid-analytics-data" PORT=80

COPY . /app
WORKDIR /app
RUN set -ex && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install Flask gunicorn
CMD exec gunicorn --bind :$PORT app:server