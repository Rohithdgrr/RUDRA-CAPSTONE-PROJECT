FROM python:3.14-slim
# WeasyPrint + Cairo/Pango stack (see WeasyPrint docs) + libffi for cffi
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi8 \
    libxml2 \
    libxslt1.1 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
# Cache-bust only on requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
# Copy only needed sources (honors .dockerignore)
COPY src ./src
COPY resources ./resources
COPY campaigns ./campaigns
COPY pyproject.toml README.md ./
# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
# Healthcheck for API
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/platforms', timeout=3).read()" || exit 1
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
