FROM python:3.7

ENV FSTYPE "gcs"
ENV BUCKET "gcs://covid-analytics-data"
COPY . /app
WORKDIR /app
RUN set -ex && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install Flask gunicorn
CMD gunicorn -b 0.0.0.0:80 app:server