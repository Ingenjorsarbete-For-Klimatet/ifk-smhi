"""Type variables."""

from typing import TypeVar

from smhi.models.mesan_model import (
    MesanCreatedTime,
    MesanGeoMultiPoint,
    MesanGeoPolygon,
    MesanMultiPoint,
    MesanParameter,
    MesanPoint,
    MesanValidTime,
)
from smhi.models.metobs_model import (
    MetobsCategoryModel,
    MetobsDataModel,
    MetobsParameterModel,
    MetobsPeriodModel,
    MetobsStationModel,
    MetobsVersionModel,
)
from smhi.models.snow_model import (
    SnowCreatedTime,
    SnowGeoMultiPoint,
    SnowGeoPolygon,
    SnowMultiPoint,
    SnowParameter,
    SnowPoint,
    SnowValidTime,
)

MetobsModels = TypeVar(
    "MetobsModels",
    MetobsCategoryModel,
    MetobsVersionModel,
    MetobsParameterModel,
    MetobsStationModel,
    MetobsPeriodModel,
    MetobsDataModel,
)

Parameter = TypeVar("Parameter", MesanParameter, SnowParameter)
ApprovedTime = TypeVar("ApprovedTime", MesanCreatedTime, SnowCreatedTime)
ValidTime = TypeVar("ValidTime", MesanValidTime, SnowValidTime)
GeoPolygon = TypeVar("GeoPolygon", MesanGeoPolygon, SnowGeoPolygon)
GeoMultiPoint = TypeVar("GeoMultiPoint", MesanGeoMultiPoint, SnowGeoMultiPoint)
Point = TypeVar("Point", MesanPoint, SnowPoint)
MultiPoint = TypeVar("MultiPoint", MesanMultiPoint, SnowMultiPoint)
