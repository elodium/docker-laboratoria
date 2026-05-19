# Sprawozdanie

**Autor:** Ihor Shypilov

---

### Opis

Aplikacja webowa zbudowana w języku Python z wykorzystaniem FastAPI. Wyświetla aktualną pogodę
dla dowolnego miasta i kraju, korzystając z bezpłatnego API [Open-Meteo](https://open-meteo.com/).

### Działanie aplikacji

![](screenshots/1.png)
![](screenshots/2.png)

Aplikacja udostępnia:
- **`GET /`** – formularz wyboru kraju i miasta
- **`POST /weather`** – przetwarza formularz, geokoduje lokalizację i pobiera pogodę

---

## 2. Dockerfile

### Dwuetapowe budowanie (multi-stage build)

```
-------------------------------      ------------------------------------
|   STAGE 1: builder          |      |   STAGE 2: runtime (obraz final) |
|   python:3.12-slim          |      |   python:3.12-slim               |
|                             |      |                                  |
|  requirements.txt           |      |  /venv  <-- skopiowany z builder |
|       |                     |      |  main.py                         |
|       |                     |      |  templates/                      |
|  pip install -> /venv ------|----->|                                  |
|                             |      |  USER appuser (non-root)         |
|  pip, wheel, kompilatory    |      |  EXPOSE 8000                     |
|  nie trafiają do STAGE 2    |      |  HEALTHCHECK                     |
-------------------------------      ------------------------------------
```

---

## Polecenia Docker

### Budowanie obrazu

```bash
docker build -f Dockerfile -t weather-app:1.0 .
```

### Uruchomienie kontenera

```bash
docker run -d \
  --name weather \
  -p 8000:8000 \
  weather-app:1.0
```

### Odczyt logów startowych

```bash
# Wszystkie logi kontenera od początku
docker logs weather

# Logi z timestamp'ami
docker logs --timestamps weather

# Logi na żywo (follow)
docker logs -f weather

# Tylko logi z momentu startu (pierwsze 20 linii)
docker logs weather | head -20
```

Wynik polecenia `docker logs weather`:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2026-05-19T22:06:44+0000 | INFO | ============================================================
2026-05-19T22:06:44+0000 | INFO | Application started
2026-05-19T22:06:44+0000 | INFO |   Date/time : 2026-05-19T22:06:44Z (UTC)
2026-05-19T22:06:44+0000 | INFO |   Author    : Ihor Shypilov
2026-05-19T22:06:44+0000 | INFO |   Host      : 96f5ffaaf7ec
2026-05-19T22:06:44+0000 | INFO |   TCP port  : 8000
2026-05-19T22:06:44+0000 | INFO | ============================================================
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Liczba warstw i rozmiar obrazu

**Rozmiar obrazu:**

```bash
docker images weather-app:1.0
```

Wynik:

```
(.venv) [elodium kolokwium]$ docker images weather-app:1.0
                                                                                                                                                  i Info →   U  In Use
IMAGE             ID             DISK USAGE   CONTENT SIZE   EXTRA
weather-app:1.0   7945c57ab672        221MB           53MB    U
```

**Liczba warstw:**

```bash
docker inspect --format='{{len .RootFS.Layers}}' weather-app:1.0
```

Wynik:

```
(.venv) [elodium kolokwium]$ docker inspect --format='{{len .RootFS.Layers}}' weather-app:1.0
9
```
