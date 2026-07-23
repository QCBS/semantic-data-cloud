FROM python:3.14.2-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 999 ontop \
    && useradd -u 999 -g 999 -c "Ontop unprivileged user" -d /opt/ontop -s /sbin/nologin ontop

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]