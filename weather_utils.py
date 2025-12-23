"""
Shared Weather Utilities

Common weather functions used by all agent framework examples.
Uses the free Open-Meteo API (no API key required).
"""

import httpx

# Open-Meteo APIs (free, no API key required)
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def geocode_city(city: str, country: str = "") -> dict:
    """Convert city name to coordinates using Open-Meteo geocoding API."""
    params = {"name": city, "count": 5, "language": "en", "format": "json"}

    with httpx.Client(timeout=10.0) as client:
        response = client.get(GEOCODING_URL, params=params)
        response.raise_for_status()
        data = response.json()

    if "results" not in data or not data["results"]:
        raise ValueError(f"City '{city}' not found. Please check the spelling.")

    results = data["results"]

    if country:
        for result in results:
            if result.get("country_code", "").upper() == country.upper():
                return result

    return results[0]


def get_weather_description(weather_code: int) -> str:
    """Convert WMO weather code to human-readable description."""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return weather_codes.get(weather_code, "Unknown")


def fetch_current_weather(city: str, country: str = "") -> str:
    """
    Fetch current weather for a city.

    Args:
        city: The city name (e.g., 'London', 'New York', 'Tokyo')
        country: Optional country code (e.g., 'US', 'UK')

    Returns:
        Formatted weather string
    """
    try:
        location = geocode_city(city, country)
        lat, lon = location["latitude"], location["longitude"]
        city_name = location["name"]
        country_name = location.get("country", "")

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "weather_code",
                "wind_speed_10m",
                "precipitation",
            ],
            "timezone": "auto",
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get(WEATHER_URL, params=params)
            response.raise_for_status()
            data = response.json()

        current = data["current"]
        units = data["current_units"]
        weather_desc = get_weather_description(current["weather_code"])

        return f"""Current Weather for {city_name}, {country_name}:
Conditions: {weather_desc}
Temperature: {current['temperature_2m']}{units['temperature_2m']}
Feels Like: {current['apparent_temperature']}{units['apparent_temperature']}
Humidity: {current['relative_humidity_2m']}{units['relative_humidity_2m']}
Wind: {current['wind_speed_10m']} {units['wind_speed_10m']}
Precipitation: {current['precipitation']} {units['precipitation']}"""

    except ValueError as e:
        return str(e)
    except httpx.HTTPError as e:
        return f"Error fetching weather data: {str(e)}"


def fetch_weather_forecast(city: str, country: str = "", days: int = 3) -> str:
    """
    Fetch weather forecast for a city.

    Args:
        city: The city name
        country: Optional country code
        days: Number of days (1-7)

    Returns:
        Formatted forecast string
    """
    try:
        days = max(1, min(7, days))
        location = geocode_city(city, country)
        lat, lon = location["latitude"], location["longitude"]
        city_name = location["name"]
        country_name = location.get("country", "")

        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "weather_code",
                "precipitation_sum",
            ],
            "timezone": "auto",
            "forecast_days": days,
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get(WEATHER_URL, params=params)
            response.raise_for_status()
            data = response.json()

        daily = data["daily"]
        units = data["daily_units"]

        result = f"{days}-Day Forecast for {city_name}, {country_name}:\n\n"

        for i in range(len(daily["time"])):
            date = daily["time"][i]
            weather_desc = get_weather_description(daily["weather_code"][i])
            result += f"""{date}: {weather_desc}
  High: {daily['temperature_2m_max'][i]}{units['temperature_2m_max']} / Low: {daily['temperature_2m_min'][i]}{units['temperature_2m_min']}
  Precipitation: {daily['precipitation_sum'][i]} {units['precipitation_sum']}

"""
        return result.strip()

    except ValueError as e:
        return str(e)
    except httpx.HTTPError as e:
        return f"Error fetching forecast data: {str(e)}"
