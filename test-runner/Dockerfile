FROM python:3.14.2-slim

WORKDIR /runner

COPY requirements.txt .

RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY . .

CMD ["pytest", "-v", "--color=yes"]