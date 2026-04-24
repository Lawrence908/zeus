# zeus/core/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# git: needed by zeus.ingest.sources.git (commit history ingest)
# libzim-dev: native library for python `libzim` bindings used by
# zeus.ingest.sources.kiwix_zim (disk ZIM → zeus_knowledge ingest)
# ripgrep: backs /vault/search (olympian_file_search)
RUN apt-get update \
 && apt-get install -y --no-install-recommends git libzim-dev ripgrep \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "zeus.core.main:app", "--host", "0.0.0.0", "--port", "8000"]
