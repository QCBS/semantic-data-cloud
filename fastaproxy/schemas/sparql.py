from datetime import date
from enum import StrEnum
#
from pydantic import BaseModel, Field, field_validator


class MaintenanceFrequency(StrEnum):
    ANNUALLY = "annually"
    AS_NEEDED = "asNeeded"
    BIANNUALLY = "biannually"
    CONTINUALLY = "continually"
    DAILY = "daily"
    IRREGULAR = "irregular"
    MONTHLY = "monthly"
    NOT_PLANNED = "notPlanned"
    OTHER_MAINTENANCE_PERIOD = "otherMaintenancePeriod"
    UNKNOWN = "unknown"
    UNKOWN = "unkown"
    WEEKLY = "weekly"


class QueryRequest(BaseModel):
    query: str
    bbox: tuple[float | None, float | None, float | None, float | None] | None  = Field(None, description="Bounding box for the desired datasets (in WGS84)")
    temporal: tuple[str | None, str | None] | None = Field(None, description="Begin and end dates for the desired datasets (in YYYY-MM-DD)")
    licenses: list[str] | None = Field(None, description="SPDX IDs of the licenses requested")
    maintenance: list[MaintenanceFrequency] | None = Field(None, description="Controlled vocabulary terms for maintenance update frequency")
    datasets: list[str] | None = Field(None, description="List of dataset IDs to be considered")


    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must not be an empty string")
        return value


    @field_validator("datasets")
    @classmethod
    def validate_datasets(cls, value: list[str] | None) -> list[str] | None:
        if value == []:
            raise ValueError("datasets must not be an empty list")
        return value


    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, value: list[float]) -> list[float]:
        if len(value) != 4:
            raise ValueError("Spatial range bbox must have exactly 4 values: [min_lon, min_lat, max_lon, max_lat]")
        min_lon, min_lat, max_lon, max_lat = value
        if min_lon > max_lon:
            raise ValueError("min_lon must be <= max_lon")
        if min_lat > max_lat:
            raise ValueError("min_lat must be <= max_lat")
        return value


    @field_validator("temporal")
    @classmethod
    def validate_temporal(cls, value: tuple[str | None, str | None] | None) -> tuple[str | None, str | None] | None:
        if value is None:
            return None

        begin, end = value

        if begin is not None:
            begin = date.fromisoformat(begin)

        if end is not None:
            end = date.fromisoformat(end)

        if begin is not None and end is not None and begin > end:
            raise ValueError("begin_date must be <= end_date")

        return value