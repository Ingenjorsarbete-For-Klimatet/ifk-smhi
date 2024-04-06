from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MetobsLinkModel(BaseModel):
    rel: str
    type: str
    href: str


class MetobsLinksModel(BaseModel):
    key: Optional[str] = None
    updated: Optional[int] = None
    title: str
    summary: str
    link: List[MetobsLinkModel]


class MetobsGeoBoxModel(BaseModel):
    min_latitude: float = Field(..., alias="minLatitude")
    min_longitude: float = Field(..., alias="minLongitude")
    max_latitude: float = Field(..., alias="maxLatitude")
    max_longitude: float = Field(..., alias="maxLongitude")


class MetobsGeoLinksModel(MetobsLinksModel):
    unit: str
    geo_box: MetobsGeoBoxModel = Field(..., alias="geoBox")


class MetobsBaseModel(BaseModel):
    key: Optional[str] = None
    updated: Optional[int] = None
    title: str
    summary: str
    link: List[MetobsLinkModel]


class MetobsCategoryModel(MetobsBaseModel):
    """Model used for versions."""

    version: List[MetobsLinksModel]

    @property
    def data(self) -> List[MetobsLinksModel]:
        return self.version


class MetobsVersionItem(BaseModel):
    key: Optional[str] = None
    title: str
    summary: str
    unit: str


class MetobsVersionModel(MetobsBaseModel):
    """Model used for parameters."""

    resource: List[MetobsGeoLinksModel]

    @field_validator("resource")
    @classmethod
    def serialise_resource_in_order(cls, resource: List[MetobsGeoLinksModel]):
        return sorted(resource, key=lambda x: int(x.key))

    @property
    def data(self) -> Tuple[MetobsVersionItem, ...]:
        return tuple(
            MetobsVersionItem(key=x.key, title=x.title, summary=x.summary, unit=x.unit)
            for x in self.resource
        )


class MetobsCodesEntryModel(BaseModel):
    key: int
    value: str


class MetobsCodesModel(BaseModel):
    entry: MetobsCodesEntryModel


class MetobsValueModel(str, Enum):
    sampling = "SAMPLING"
    interval = "INTERVAL"


class MetobsMeasuringStationsModel(str, Enum):
    core = "CORE"
    additional = "ADDITIONAL"


class MetobsStationLinkModel(MetobsLinksModel):
    name: str
    owner: str
    owner_category: str = Field(..., alias="ownerCategory")
    measuring_stations: MetobsMeasuringStationsModel = Field(
        ..., alias="measuringStations"
    )
    id: int
    height: float
    latitude: float
    longitude: float
    active: bool
    from_: int = Field(..., alias="from")
    to: int


class MetobsParameterModel(MetobsBaseModel):
    """Model used for stations."""

    unit: str
    value_type: MetobsValueModel = Field(..., alias="valueType")
    station_set: List[MetobsLinksModel] = Field(..., alias="stationSet")
    station: List[MetobsStationLinkModel]

    @field_validator("station")
    @classmethod
    def serialise_station_in_order(cls, station: List[MetobsStationLinkModel]):
        return sorted(station, key=lambda x: int(x.id))

    @property
    def data(self) -> Tuple[Tuple[int, str], ...]:
        return tuple((x.id, x.name) for x in self.station)


class MetobsPositionItem(BaseModel):
    from_: int = Field(..., alias="from")
    to: int
    height: float
    latitude: float
    longitude: float


class MetobsStationModel(MetobsBaseModel):
    """Model used for periods."""

    owner: Optional[str] = None
    owner_category: Optional[str] = Field(default=None, alias="ownerCategory")
    measuring_stations: Optional[MetobsMeasuringStationsModel] = Field(
        default=None, alias="measuringStations"
    )
    active: Optional[bool] = None
    from_: Optional[int] = Field(default=None, alias="from")
    to: Optional[int] = None
    position: Optional[List[MetobsPositionItem]] = None
    period: List[MetobsLinksModel]

    @field_validator("period")
    @classmethod
    def serialise_period_in_order(cls, period: List[MetobsLinksModel]):
        return sorted(period, key=lambda x: x.key)

    @property
    def data(self) -> Tuple[Optional[str], ...]:
        return tuple(x.key for x in self.period)


class MetobsPeriodModel(MetobsBaseModel):
    """Model used for stations."""

    from_: int = Field(..., alias="from")
    to: int
    data: List[MetobsLinksModel]


class MetobsDataModel(BaseModel):
    """Data model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    station: Optional[pd.DataFrame] = None
    parameter: Optional[pd.DataFrame] = None
    period: Optional[pd.DataFrame] = None
    stationdata: Optional[pd.DataFrame] = None
