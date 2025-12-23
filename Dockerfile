ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim AS builder

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc \
    && python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential gcc && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY package.json tailwind.config.js postcss.config.js /app/
COPY static/ /app/static/

RUN npm install && npm run build

FROM python:${PYTHON_VERSION}-slim AS runtime

ARG UID=10001
RUN adduser --disabled-password --gecos "" --uid ${UID} appuser

WORKDIR /app

COPY --from=builder /usr/local/ /usr/local/
COPY --from=builder /app /app
COPY . /app

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 6969
CMD ["gunicorn", "--bind", "0.0.0.0:6969", "app:create_app()", "--workers", "2", "--threads", "4"]
