# etap pierwszy
FROM golang:1.26-alpine3.23 AS builder

WORKDIR /app

COPY . .

ARG VERSION=dev

# przekazanie wersji w Go poprzez ldflags
RUN go build -ldflags="-X main.version=${VERSION}" -o app


# etap drugi
FROM nginx:1.25-alpine

WORKDIR /app

# kopiowanie aplikacji z build stage
COPY --from=builder /app/app /app/app

# usuwanie domyślnego pliku konfiguracji w kontenerze
RUN rm /etc/nginx/conf.d/default.conf
# kopiowanie ręcznie stworzonego default.conf
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# HEALTHCHECK sprawdzajacy endpoint aplikacji Go
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/ || exit 1

# uruchamiamy zarowno go, jak i nginx
CMD ["/bin/sh", "-c", "/app/app & nginx -g 'daemon off;'"]
