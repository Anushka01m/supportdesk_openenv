FROM python:3.11-slim

WORKDIR /app
COPY . .
ENV PYTHONPATH=/app

# Increase pip timeout to avoid network timeouts on large deps (gradio, etc.)
ENV PIP_DEFAULT_TIMEOUT=300

RUN pip install --upgrade pip \
    && pip install --no-cache-dir openenv-core fastapi uvicorn

EXPOSE 8000

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]