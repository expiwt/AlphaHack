# Multi-stage Docker для docker-compose
FROM docker:latest

WORKDIR /app

COPY docker-compose.yml .
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Установи docker-compose
RUN apk add --no-cache python3 py3-pip && \
    pip install docker-compose

EXPOSE 8000 5173 5432 6379

CMD ["docker-compose", "up"]
