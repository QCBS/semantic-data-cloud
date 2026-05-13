FROM ghcr.io/osgeo/gdal:ubuntu-small-latest
WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip python3-venv

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN python3 -m venv /opt/venv && \
	/opt/venv/bin/pip install --upgrade pip && \
	/opt/venv/bin/pip install -r requirements.txt

COPY . .