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
from smhi.models.metobs_data import MetobsDataModel
from smhi.models.metobs_parameters import MetobsParameterModel
from smhi.models.metobs_periods import MetobsPeriodModel
from smhi.models.metobs_stations import MetobsStationModel
from smhi.models.metobs_versions import MetobsVersionModel

MetobsModels = TypeVar(
    "MetobsModels",
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
