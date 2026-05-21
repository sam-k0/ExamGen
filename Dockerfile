# build stage
FROM python:3.12-slim AS builder

WORKDIR /build
RUN python -m pip install poetry

COPY . /build
RUN poetry self add poetry-plugin-export
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN mkdir /wheels && pip download --no-cache-dir -r requirements.txt -d /wheels

#final stage
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y fonts-nanum && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /build/requirements.txt /tmp/requirements.txt
COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir --no-index --find-links /wheels -r /tmp/requirements.txt
RUN rm -rf /wheels /tmp/requirements.txt

COPY src/examgen /app/examgen

RUN mkdir -p /app/pdfs

EXPOSE 5000

ENV PYTHONPATH=/app

CMD ["python", "-m", "examgen.main"]