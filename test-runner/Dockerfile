FROM python:3.14.2-slim

WORKDIR /runner

COPY . .

RUN pip install --no-cache-dir --require-hashes -r requirements.txt

CMD ["pytest", "-v", "--color=yes"]