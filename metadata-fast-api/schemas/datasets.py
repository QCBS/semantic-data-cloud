from datetime import date
#
from pydantic import BaseModel, Field


class DatasetRequest(BaseModel):
    min_lon: float = Field(-180.0, description="West bound of query bbox (in WGS84)", ge=-180.0, le=180.0)
    min_lat: float = Field(-90.0, description="South bound of query bbox (in WGS84)", ge=-90.0, le=90.0)
    max_lon: float = Field(180.0, description="East bound of query bbox (in WGS84)", ge=-180.0, le=180.0)
    max_lat: float = Field(90.0, description="North bound of query bbox (in WGS84)", ge=-90.0, le=90.0)
    begin_date: date = Field(date(1, 1, 1), description="Start of temporal range (YYYY-MM-DD)")
    end_date: date = Field(date(2038, 1, 19), description="End of temporal range (YYYY-MM-DD)")
    licenses: list[str] | None = Field(None, description="SPDX IDs of the licenses requested")
    maintenance: list[str] | None = Field(None, description="Controlled vocabulary terms for maintenance update frequency")