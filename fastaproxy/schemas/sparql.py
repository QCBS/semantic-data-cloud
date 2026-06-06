from datetime import date
#
from pydantic import BaseModel, field_validator

class QueryRequest(BaseModel):
    query: str
    bbox: list[float] = [-180.0, -90.0, 180.0, 90.0]
    temporal: list[str] = ["0001-01-01", "2038-01-19"]
    licenses: list[str] = None

    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, value: list[float]) -> list[float]:
        if len(value) != 4:
            raise ValueError("Spatial range bbox must have exactly 4 values: [min_lon, min_lat, max_lon, max_lat]")
        min_lon, min_lat, max_lon, max_lat = value
        if min_lon > max_lon:
            raise ValueError("min_lon must be ≤ max_lon")
        if min_lat > max_lat:
            raise ValueError("min_lat must be ≤ max_lat")
        return value

    @field_validator("temporal")
    @classmethod
    def validate_temporal(cls, value: list[str]) -> list[str]:
        if len(value) != 2:
            raise ValueError("Temporal range must have exactly 2 values: [begin_date, end_date]")
        try:
            begin = date.fromisoformat(value[0])
            end = date.fromisoformat(value[1])
        except ValueError:
            raise ValueError("dates must be in YYYY-MM-DD format")
        if begin > end:
            raise ValueError("begin_date must be ≤ end_date")
        return value


