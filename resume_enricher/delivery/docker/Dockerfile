# Resume Enricher — container image for the HTTP API.
#
# Build context is the REPO ROOT (the outer `resume_enricher/` folder that holds
# main.py, requirements.txt and the `resume_enricher/` package). The docker-compose
# file next to this one already points the context there.

FROM python:3.11-slim

# Don't buffer logs, don't write .pyc files — nicer in a container.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 1. Install dependencies first (this layer is cached until requirements change).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the application package.
COPY resume_enricher ./resume_enricher

# 3. Serve the API. 0.0.0.0 so it's reachable from outside the container.
EXPOSE 8000
CMD ["uvicorn", "resume_enricher.delivery.api:app", "--host", "0.0.0.0", "--port", "8000"]
