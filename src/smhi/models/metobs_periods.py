# generated by datamodel-codegen:
#   filename:  https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1/station/1.json
#   timestamp: 2024-03-23T21:07:53+00:00

from __future__ import annotations

from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator


class PositionItem(BaseModel):
    from_: int = Field(..., alias="from")
    to: int
    height: float
    latitude: float
    longitude: float


class LinkItem(BaseModel):
    href: str
    rel: str
    type: str


class PeriodItem(BaseModel):
    key: Optional[str] = None
    updated: Optional[int] = None
    title: str
    summary: str
    link: List[LinkItem]


class PeriodModel(BaseModel):
    key: Optional[str] = None
    updated: Optional[int] = None
    title: str
    owner: Optional[str] = None
    owner_category: Optional[str] = Field(default=None, alias="ownerCategory")
    measuring_stations: Optional[str] = Field(default=None, alias="measuringStations")
    active: Optional[bool] = None
    summary: str
    from_: Optional[int] = Field(default=None, alias="from")
    to: Optional[int] = None
    position: Optional[List[PositionItem]] = None
    link: List[LinkItem]
    period: List[PeriodItem]

    @field_validator("period")
    @classmethod
    def serialise_period_in_order(cls, period: List[PeriodItem]):
        return sorted(period, key=lambda x: x.key)

    @property
    def data(self) -> Tuple[Optional[str], ...]:
        return tuple(x.key for x in self.period)
