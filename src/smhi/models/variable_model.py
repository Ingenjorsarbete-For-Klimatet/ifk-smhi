"""Type variables."""

from typing import TypeVar

from smhi.models.mesan_model import (
    MesanApprovedTime,
    MesanMultiPointData,
    MesanParameters,
    MesanPointData,
    MesanPolygon,
    MesanValidTime,
)
from smhi.models.metfcts_model import (
    MetfctsApprovedTime,
    MetfctsMultiPointData,
    MetfctsParameters,
    MetfctsPointData,
    MetfctsPolygon,
    MetfctsValidTime,
)
from smhi.models.metobs_data import DataModel
from smhi.models.metobs_parameters import ParameterModel
from smhi.models.metobs_periods import PeriodModel
from smhi.models.metobs_stations import StationModel
from smhi.models.metobs_versions import VersionModel

MetobsModels = TypeVar(
    "MetobsModels", VersionModel, ParameterModel, StationModel, PeriodModel, DataModel
)

Parameters = TypeVar("Parameters", MesanParameters, MetfctsParameters)
ApprovedTime = TypeVar("ApprovedTime", MesanApprovedTime, MetfctsApprovedTime)
ValidTime = TypeVar("ValidTime", MesanValidTime, MetfctsValidTime)
Polygon = TypeVar("Polygon", MesanPolygon, MetfctsPolygon)
PointData = TypeVar("PointData", MesanPointData, MetfctsPointData)
MultiPointData = TypeVar("MultiPointData", MesanMultiPointData, MetfctsMultiPointData)
