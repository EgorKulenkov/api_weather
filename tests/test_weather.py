import pytest
from unittest.mock import patch
from httpx import AsyncClient

from src.utils import limiter
limiter.history.clear()

MOCK_WEATHER_RESPONSE = {
    "temperature": 15.0,
    "feels_like": 14.0,
    "humidity": 70,
    "description": "Ясно"
}

@pytest.mark.asyncio
@patch("src.main.fetch_weather_from_api")
async def test_cache_logic(mock_fetch, client: AsyncClient):
    """test API request and returning from cache"""
    mock_fetch.return_value = MOCK_WEATHER_RESPONSE

    response_1 = await client.get("/get_weather?city=Minsk&unit=celsius")
    assert response_1.status_code == 200
    data_1 = response_1.json()
    assert data_1["is_cached"] is False
    assert mock_fetch.call_count == 1

    response_2 = await client.get("/get_weather?city=Minsk&unit=celsius")
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2["is_cached"] is True
    assert mock_fetch.call_count == 1


@pytest.mark.asyncio
@patch("src.main.fetch_weather_from_api")
async def test_history_filtering_and_pagination(mock_fetch, client: AsyncClient):
    """test pagination and case-insensitive string"""
    mock_fetch.return_value = MOCK_WEATHER_RESPONSE

    await client.get("/get_weather?city=Vitebsk")
    await client.get("/get_weather?city=Brest")
    await client.get("/get_weather?city=Mogilev")

    history_resp = await client.get("/history?page=1&size=2")
    assert history_resp.status_code == 200
    history_data = history_resp.json()
    assert history_data["total_items"] == 3
    assert len(history_data["items"]) == 2

    filter_resp = await client.get("/history?city=bRe")
    filter_data = filter_resp.json()
    assert filter_data["total_items"] == 1
    assert filter_data["items"][0]["city_name"] == "Brest"
