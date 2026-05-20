from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class WeatherResponse(BaseModel):
    city_name: str = Field(..., examples=["Minsk"])
    temperature: float = Field(..., examples=[15.5])
    feels_like: float = Field(..., examples=[14.0])
    humidity: int = Field(..., examples=[70])
    unit: str = Field(..., examples=["celsius"])
    is_cached: bool = Field(..., description="Cached flag")

class WeatherHistoryItem(BaseModel):
    id: int
    city_name: str
    timestamp: datetime
    temperature: float
    feels_like: float
    humidity: int
    unit: str
    is_cached: bool

    model_config = ConfigDict(from_attributes=True)


class PaginatedHistoryResponse(BaseModel):
    total_items: int
    page: int
    size: int
    items: list[WeatherHistoryItem]
