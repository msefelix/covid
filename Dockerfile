FROM python:3.7
ENV FSTYPE="gcs" BUCKET="gs://covid-analytics-data" PORT=8080

RUN set -ex && \
    python3 -m pip install --upgrade pip && \
    pip install gsutil && \
    pip install dash==2.1.0 && \
    pip install dash-bootstrap-components==1.0.2 && \
    pip install fastparquet && \
    pip install gcsfs==2022.1.0 && \
    pip install geopandas==0.9.0 && \
    pip install lxml==4.7.1 && \
    pip install pandas==1.1.4 && \
    pip install plotly==5.5.0 && \
    pip install pyarrow==4.0.1 && \
    pip install requests==2.25.1 && \
    pip install Flask gunicorn

COPY . /app
WORKDIR /app
RUN pip install git+https://github.com/msefelix/covid.git
CMD ["./start.sh"]