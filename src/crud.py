from src.models import WeatherQuery

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

async def create_weather_query(db: AsyncSession,
                               city_name: str,
                               weather_data: dict,
                               unit: str,
                               is_cached: bool) -> WeatherQuery:
    db_query = WeatherQuery(
            city_name=city_name.capitalize(),
            temperature=weather_data["temperature"],
            feels_like=weather_data["feels_like"],
            humidity=weather_data["humidity"],
            unit=unit,
            is_cached=is_cached)

    db.add(db_query)
    await db.commit()
    await db.refresh(db_query)

    return db_query


async def get_weather_query(db: AsyncSession,
                            city_name: str) -> WeatherQuery | None:
    db_query = (
            select(WeatherQuery)
            .where(WeatherQuery.city_name==city_name)
            .order_by(WeatherQuery.timestamp.desc())
            .limit(1)
            )

    result = await db.execute(db_query)
    return result.scalar_one_or_none()


async def get_weather_history(db: AsyncSession,
                              city: str,
                              from_date: datetime,
                              to_date: datetime,
                              page: int = 1,
                              size: int = 10) -> tuple[int, list[WeatherQuery]]:
    stmt = select(WeatherQuery).order_by(WeatherQuery.timestamp.desc())
    count_stmt = select(func.count()).select_from(WeatherQuery)

    if city:
        filter_condition = WeatherQuery.city_name.ilike(f"%{city}%")
        stmt = stmt.where(filter_condition)
        count_stmt = count_stmt.where(filter_condition)

    if from_date:
        stmt = stmt.where(WeatherQuery.timestamp >= from_date)
        count_stmt = count_stmt.where(WeatherQuery.timestamp >= from_date)
    if to_date:
        stmt = stmt.where(WeatherQuery.timestamp <= to_date)
        count_stmt = count_stmt.where(WeatherQuery.timestamp >= from_date)
    if to_date:
        stmt = stmt.where(WeatherQuery.timestamp <= to_date)
        count_stmt = count_stmt.where(WeatherQuery.timestamp <= to_date)

    total_result = await db.execute(count_stmt)
    total_items = total_result.scalar_one()

    offset = (page - 1) * size
    stmt = stmt.offset(offset).limit(size)

    result = await db.execute(stmt)
    items = result.scalars().all()

    return total_items, list(items)



async def get_filtered_history(db: AsyncSession,
                               city: str | None = None,
                               from_date: datetime | None = None,
                               to_date: datetime | None = None) -> list[WeatherQuery]:
    stmt = select(WeatherQuery).order_by(WeatherQuery.timestamp.desc())

    if city:
        stmt = stmt.where(WeatheQuery.city_name.ilike(f"%{city}%"))
    if from_date:
        stmt = stmt.where(WeatherQuery.timestamp >= from_date)
    if to_date:
        stmt = stmt.where(WeatherQuery.timestamp <= to_date)

    result = await db.execute(stmt)
    return list(result.scalars().all())
