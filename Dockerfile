FROM python:3.7
ENV FSTYPE="gcs" BUCKET="gs://covid-analytics-data" PORT=8080
RUN set -ex && \
    chmod +x ./start.sh && \
    python3 -m pip install --upgrade pip && \
    pip install gsutil && \
    pip install -r requirements.txt && \
    pip install Flask gunicorn

COPY . /app
WORKDIR /app

CMD ["./start.sh"]