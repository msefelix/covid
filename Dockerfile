FROM python:3.7

ENV FSTYPE="gcs" BUCKET="gs://covid-analytics-data" PORT=8080

COPY . /app
WORKDIR /app

RUN set -ex && \
    chmod +x /start.sh && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install Flask gunicorn

CMD ["/start.sh"]