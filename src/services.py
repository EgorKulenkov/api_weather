import time
import httpx
from fastapi import HTTPException, status, Depends

from src.database import get_db
from src.models import WeatherQuery
from src.config import settings

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = settings.API_KEY

async def fetch_weather_from_api(city_name: str, api_key: str, units: str = "metric"):
    api_units = "imperial" if units == "fahrenheit" else "metric"

    params = {
        "q": city_name,
        "appid": api_key,
        "units": api_units,
        "lang": "ru"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(WEATHER_URL, params=params, timeout=5.0)

        except httpx.RequestError as ex:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detai=f"There is some problem :( {exc}")
        
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"City {city_name} is not found")
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail=f"Error: {response.status_code}")

        data = response.json()

        weather_data = {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
        }

        return weather_data

