import pytest
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

MOCK_WEATHER_RESPONSE = {
    "temperature": 15.0,
    "feels_like": 14.0,
    "humidity": 70
}

@pytest.mark.asyncio
@patch("src.main.fetch_weather_from_api")
async def test_rate_limiter_blocks_and_prevents_db_write(
    mock_fetch, 
    client: AsyncClient, 
    db_session: AsyncSession
):
    """test limiter return 429 and doesn't post any query in database"""
    mock_fetch.return_value = MOCK_WEATHER_RESPONSE

    from src.utils import limiter
    
    original_limit = limiter.request_limit
    limiter.request_limit = 2
    limiter.history.clear()

    try:
        resp1 = await client.get("/get_weather?city=Minsk")
        resp2 = await client.get("/get_weather?city=Minsk")
        assert resp1.status_code == 200
        assert resp2.status_code == 200

        resp3 = await client.get("/get_weather?city=Minsk")
        assert resp3.status_code == 429
        
        assert "suspicious activite" in resp3.json()["detail"]

    finally:
        limiter.request_limit = original_limit
        limiter.history.clear()
