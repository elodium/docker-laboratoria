import logging
import socket
from datetime import datetime, timezone
 
import httpx
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Logging – simple format: time | level | message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
logger = logging.getLogger(__name__)
 

APP_PORT = 8000
AUTHOR = "Ihor Shypilov"
 
app = FastAPI(title="Weather App")
templates = Jinja2Templates(directory="templates")
 
 
@app.on_event("startup")
async def startup_event() -> None:
    """Log startup info (requirement 1a):
    - current UTC date/time
    - author name
    - TCP port the server listens on
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    hostname = socket.gethostname()
    logger.info("=" * 60)
    logger.info("Application started")
    logger.info("  Date/time : %s (UTC)", now)
    logger.info("  Author    : %s", AUTHOR)
    logger.info("  Host      : %s", hostname)
    logger.info("  TCP port  : %d", APP_PORT)
    logger.info("=" * 60)
    

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Docs: https://open-meteo.com/en/docs#weathervariables
WMO_CODES = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Icy Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"),
    53: ("Drizzle", "🌦️"),
    55: ("Heavy Drizzle", "🌧️"),
    61: ("Light Rain", "🌧️"),
    63: ("Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    71: ("Light Snow", "🌨️"),
    73: ("Snow", "❄️"),
    75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "🌨️"),
    80: ("Rain Showers", "🌦️"),
    81: ("Showers", "🌦️"),
    82: ("Violent Showers", "⛈️"),
    85: ("Snow Showers", "🌨️"),
    86: ("Heavy Snow Showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm w/ Hail", "⛈️"),
    99: ("Thunderstorm w/ Heavy Hail", "⛈️"),
}

WIND_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def wind_direction_label(degrees: float) -> str:
    """Convert a wind bearing (0-360 deg) into a readable abbreviation from WIND DIRECTIONS list"""
    idx = round(degrees / 45) % 8
    return WIND_DIRECTIONS[idx]


async def geocode(city: str, country: str) -> dict | None:
    """Convert a city + country string to geographic coordinates

    Queries the Open-Meteo geocoding API with the city name and returns
    the best matching result. Results are filtered by country name or
    ISO country code first; if no exact country match is found, the
    top result is returned as a fallback
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GEOCODE_URL,
            params={"name": city, "count": 10, "language": "en", "format": "json"},
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results", [])
    if not results:
        return None

    # Try to match by country name or 2-letter ISO code (case-insensitive)
    country_lower = country.strip().lower()
    for r in results:
        if (
            r.get("country", "").lower() == country_lower
            or r.get("country_code", "").lower() == country_lower
        ):
            return r

    # No country match - return the highest-ranked result anyway
    return results[0]


async def get_weather(lat: float, lon: float) -> dict:
    """Fetch current weather conditions for a given coordinate pair

    Calls the Open-Meteo forecast API requesting only the 'current'
    block (no hourly/daily data), for the response to stay small.
    The timezone is set to 'auto', returned timestamps reflect
    local time at the requested location
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        # Request only the variables to display in the template
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "weathercode",
            "windspeed_10m",
            "winddirection_10m",
            "precipitation",
            "surface_pressure",
            "visibility",
            "uv_index",
        ],
        "timezone": "auto",  # Use the local location timezone
        "wind_speed_unit": "kmh",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(WEATHER_URL, params=params)
        resp.raise_for_status()
        return resp.json()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the empty search form"""
    return templates.TemplateResponse(request, "weather.html")


@app.post("/weather", response_class=HTMLResponse)
async def weather(
    request: Request,
    city: str = Form(...),
    country: str = Form(...),
):
    """Handle the weather search form submission

    - Gets coordinates of the submitted city + country (geocode func)
    - Fetches current weather for those coordinates (get_weather func)
    - Converts the raw API data into a flat dict for the template
    - Rerenders the page with data or an error message
    """
    error = None
    weather_data = None

    try:
        location = await geocode(city, country)

        if not location:
            error = f'Could not find "{city}, {country}". Please check the spelling and try again.'
        else:
            raw = await get_weather(location["latitude"], location["longitude"])
            current = raw["current"]

            # Map the WMO weather code to a label + emoji
            code = current.get("weathercode", 0)
            condition, emoji = WMO_CODES.get(code, ("Unknown", "🌡️"))

            # Build the dict fot the Jinja2 template
            weather_data = {
                "city": location.get("name", city),
                "country": location.get("country", country),
                "timezone": raw.get("timezone", ""),
                "temp": round(current["temperature_2m"]),
                "feels_like": round(current["apparent_temperature"]),
                "humidity": current["relative_humidity_2m"],
                "condition": condition,
                "emoji": emoji,
                "wind_speed": round(current["windspeed_10m"]),
                "wind_dir": wind_direction_label(current["winddirection_10m"]),
                "precipitation": current["precipitation"],
                "pressure": round(current["surface_pressure"]),
                # API returns visibility in metres, converting to kilometres
                "visibility": round(current.get("visibility", 0) / 1000, 1),
                "uv_index": current.get("uv_index", 0),
                "lat": round(location["latitude"], 4),
                "lon": round(location["longitude"], 4),
            }

    except httpx.HTTPError as exc:
        error = f"Network error while fetching weather data: {exc}"
    except Exception as exc:
        error = f"Unexpected error: {exc}"

    return templates.TemplateResponse(
        request,
        "weather.html",
        {"weather": weather_data, "error": error, "city": city, "country": country},
    )
