"""Type variables."""

from typing import TypeVar

from smhi.models.mesan_model import (
    MesanApprovedTime,
    MesanGeoMultiPoint,
    MesanGeoPolygon,
    MesanMultiPointModel,
    MesanParameter,
    MesanPointModel,
    MesanValidTime,
)
from smhi.models.metfcts_model import (
    MetfctsApprovedTime,
    MetfctsGeoMultiPoint,
    MetfctsGeoPolygon,
    MetfctsMultiPointModel,
    MetfctsParameter,
    MetfctsPointModel,
    MetfctsValidTime,
)
from smhi.models.metobs_model import (
    MetobsCategoryModel,
    MetobsDataModel,
    MetobsParameterModel,
    MetobsPeriodModel,
    MetobsStationModel,
    MetobsVersionModel,
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

Parameter = TypeVar("Parameter", MesanParameter, MetfctsParameter)
ApprovedTime = TypeVar("ApprovedTime", MesanApprovedTime, MetfctsApprovedTime)
ValidTime = TypeVar("ValidTime", MesanValidTime, MetfctsValidTime)
GeoPolygon = TypeVar("GeoPolygon", MesanGeoPolygon, MetfctsGeoPolygon)
GeoMultiPoint = TypeVar("GeoMultiPoint", MesanGeoMultiPoint, MetfctsGeoMultiPoint)
PointModel = TypeVar("PointModel", MesanPointModel, MetfctsPointModel)
MultiPointModel = TypeVar(
    "MultiPointModel", MesanMultiPointModel, MetfctsMultiPointModel
)
