from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta

import src.models

from src.database import init_models, async_session, engine, get_db
from src.services import fetch_weather_from_api
from src.config import settings
from src.schemas import WeatherResponse, PaginatedHistoryResponse
from src.crud import create_weather_query, get_weather_query, get_weather_history, get_filtered_history
from src.utils import limiter

from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

API_KEY = settings.API_KEY

@asynccontextmanager
async def lifespan(app: FastAPI):
    #await init_models()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "OK"}

@app.get("/check_db")
async def check_db(db: AsyncSession = Depends(get_db)):
    try:
        res = await db.execute(text("SELECT 1"))
        return {"status": "ok", "details": res.scalars()}
    except Exception as e:
        return {"error": f"{e}"}


@app.get("/get_weather")
async def get_weather(
        request: Request, 
        city: str = Query(..., min_length=2),
        unit: str = Query("celsius", pattern="^(celsius|fahrenheit)$"),
        db: AsyncSession = Depends(get_db),
        rate_limit: None = Depends(limiter.check_limit)
        ):

    weather_data = None
    from_cached = None

    latest_query = await get_weather_query(db, city)
    if latest_query:
        now = datetime.now()
        time_difference = now - latest_query.timestamp

        if time_difference < timedelta(minutes=5):
            weather_data = {
                    "temperature": latest_query.temperature,
                    "feels_like": latest_query.feels_like,
                    "humidity": latest_query.humidity
                    }
            from_cached = True

    if not weather_data:
        weather_data = await fetch_weather_from_api(
                city_name=city,
                api_key=API_KEY,
                units=unit
                )

    saved_query = await create_weather_query(db=db,
                                             city_name=city,
                                             weather_data=weather_data,
                                             unit=unit,
                                             is_cached=from_cached)
    
    response = WeatherResponse(
            city_name = saved_query.city_name,
            temperature = saved_query.temperature,
            feels_like = saved_query.feels_like,
            humidity = saved_query.humidity,
            unit = saved_query.unit,
            is_cached = saved_query.is_cached
            )

    return response


@app.get("/history")
async def get_history(city: str | None = Query(None, description="City filter"),
                      from_date: datetime | None = Query(None, description="From date"),
                      to_date: datetime | None = Query(None, description="To date"),
                      page: int = Query(1, ge=1, description="Page number"),
                      size: int = Query(1, ge=1, le=100, description="Page size"),
                      db: AsyncSession = Depends(get_db)):
    total_items, items = await get_weather_history(db=db, city=city, from_date=from_date,
                                                   to_date=to_date, page=page, size=size)
    return PaginatedHistoryResponse(
            total_items=total_items,
            page=page,
            size=size,
            items=items
            )


@app.get("/history/export-csv")
async def export_history_csv(city: str | None = Query(None, description="City filter"),
                             from_date: datetime | None = Query(None, description="From date"),
                             to_date: datetime | None = Query(None, description="To date"),
                             db: AsyncSession = Depends(get_db)):
    records = await get_filtered_history(db=db, city=city,
                                         from_date=from_date, to_date=to_date)

    def csv_generator():
        output = io.StringIO()
        writer = csv.writer(output, dialect="excel")
        
        writer.writerow([
            "ID", "City Name", "Timestamp", "Temperature", 
            "Feels Like", "Humidity", "Served From Cache", "Unit"
        ])
        
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        for record in records:
            writer.writerow([
                record.id,
                record.city_name,
                record.timestamp.strftime("%Y-%m-%d %H:%M:%S") if record.timestamp else "",
                record.temperature,
                record.feels_like,
                record.humidity,
                "Yes" if record.is_cached else "No",
                record.unit
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    filename = f"weather_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        csv_generator(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

