FROM python:3.7

ENV DASH_DEBUG_MODE True

COPY . /app
WORKDIR /app

RUN set -ex && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install Flask gunicorn

CMD exec gunicorn --bind :$PORT main:app