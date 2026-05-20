from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Float, Boolean, func

from src.database import Base

class WeatherQuery(Base):
    __tablename__ = "weather_queries"

    id: Mapped[int] = mapped_column(primary_key=True)

    city_name: Mapped[str] = mapped_column(String(100), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    temperature: Mapped[float] = mapped_column(Float)
    feels_like: Mapped[float] = mapped_column(Float)
    humidity: Mapped[int] = mapped_column()
    
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    unit: Mapped[str] = mapped_column(String(10))

