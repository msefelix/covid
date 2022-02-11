FROM python:3.7

ENV DASH_DEBUG_MODE True
COPY ./cofli /app
WORKDIR /app
RUN set -ex && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt
EXPOSE 8050
CMD ["python", "app.py"]