ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc \
    && python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential gcc && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PORT=6969
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG UID=10001
RUN adduser --disabled-password --gecos "" --uid ${UID} appuser

WORKDIR /app
COPY --from=builder /usr/local/ /usr/local/
COPY . /app

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 6969
CMD ["gunicorn", "--bind", "0.0.0.0:6969", "app:app", "--workers", "2", "--threads", "4"]
