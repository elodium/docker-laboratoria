# === builder ===
# Instalacja zależności pythona w /venv bez zostawiania pip/wheel
# w obrazie końcowym
FROM python:3.12-slim AS builder

# Ustawienie zmiennych środowiskowych tak, aby pip nie tworzył cache (.pyc, __pycache__)
# i nie buforował kół na dysku
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Kopiowanie samego pliku z bibliotekami na początku żeby uniknąć ponownego 
# pobierania wszystkiego przy każdej zmianie w kodzie aplikacji
COPY requirements.txt .

# Tworzenie wirtualnego środowiska i instalacja bibliotek z /venv
RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install -r requirements.txt

# === runtime ===
# Tworzenie małego obrazu poprzez wyciągnięcie z buildera tylko niezbędnych elementów
FROM python:3.12-slim AS runtime

# Metadane OCI
LABEL org.opencontainers.image.authors="Ihor Shypilov" \
      org.opencontainers.image.title="Weather App" \
      org.opencontainers.image.description="FastAPI weather application using Open-Meteo API" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.base.name="python:3.12-slim"

# PYTHONDONTWRITEBYTECODE - brak śmieciowych plików .pyc w kontenerze
# PYTHONUNBUFFERED - wysyłanie logów na bieżąco, bez czekania
# PATH - automatyczne używanie pythona z venv przez system
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# Tworzenie zwykłego użytkownika żeby nie uruchamiać aplikację jako root
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# Kopiujemy venv z etapu buildera (tylko to jest potrzebne z etapu pierwszego)
# pip, wheel i inne narzędzia budowania nie trafiają do obrazu finalnego
COPY --from=builder /venv /venv

# Kopiowanie kodu + jednoczesne nadanie praw dostępu dla nowego użytkownika
COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser templates/ ./templates/

# Przełączenie na zwykłego użytkownika przed startem
USER appuser

# Informacja o działaniu uvicorn na porcie 8000
EXPOSE 8000

# Healthcheck co 30 sekund czy aplikacja odpowiada na /
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" \
    || exit 1

# --host 0.0.0.0  - nasłuchiwanie połączeń z zewnątrz kontenera
# --port 8000 - uruchomienie na porcie 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]