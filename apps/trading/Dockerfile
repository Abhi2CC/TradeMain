FROM python:3.12-slim-bookworm AS runner

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/* \
  && adduser --disabled-password --gecos "" appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY auth ./auth
COPY analytics ./analytics
COPY config ./config
COPY core ./core
COPY data ./data
COPY levels ./levels
COPY storage ./storage
COPY main.py ./

RUN mkdir -p /app/storage /app/logs \
  && chown -R appuser:appuser /app

USER appuser

VOLUME ["/app/storage", "/app/logs"]

CMD ["python", "main.py"]
