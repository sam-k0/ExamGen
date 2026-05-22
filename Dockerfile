# build stage
FROM python:3.12-alpine AS builder

WORKDIR /build

RUN pip install --no-cache-dir poetry \
    && poetry self add poetry-plugin-export

COPY . /build

RUN poetry export -f requirements.txt \
    --output requirements.txt \
    --without-hashes \
    --without dev


# final stage
FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache \
    fontconfig \
    font-noto-cjk

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY --from=builder /build/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /tmp/requirements.txt

COPY src/examgen /app/examgen

RUN mkdir -p /app/pdfs

EXPOSE 5000

CMD ["python", "-m", "examgen.main"]