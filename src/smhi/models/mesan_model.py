from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Index, Series
from pydantic import BaseModel, ConfigDict, Field


class MesanValidTime(BaseModel):
    url: str
    status: int
    headers: Dict[str, str]
    valid_time: List[datetime]


class MesanApprovedTime(BaseModel):
    url: str
    status: int
    headers: Dict[str, str]
    approved_time: datetime
    reference_time: datetime


class MesanGeoPolygon(BaseModel):
    url: str
    status: int
    headers: Dict[str, str]
    type_: str = Field(..., alias="type")
    coordinates: List[List[List[float]]]


class MesanGeoMultiPoint(BaseModel):
    url: str
    status: int
    headers: Dict[str, str]
    type_: str = Field(..., alias="type")
    coordinates: List[List[float]]


class MesanParameterItem(BaseModel):
    name: str
    key: str
    level_type: str = Field(..., alias="levelType")
    level: int
    unit: str
    missing_value: int = Field(..., alias="missingValue")


class MesanParameter(BaseModel):
    url: str
    status: int
    headers: Dict[str, str]
    parameter: List[MesanParameterItem]


class MesanPointInfoSchema(pa.DataFrameModel):
    name: Index[str] = pa.Field(check_name=True, unique=True)
    level: Series[int]
    level_type: Series[str]
    unit: Series[str]


class MesanMultiPointSchema(pa.DataFrameModel):
    lat: Optional[Series[float]]
    lon: Optional[Series[float]]
    value: Series[float]


class MesanGeometry(BaseModel):
    type_: str = Field(..., alias="type")
    coordinates: List[List[float]]


class MesanPoint(BaseModel):
    """Point model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    longitude: float
    latitude: float
    url: str
    approved_time: datetime
    reference_time: datetime
    level_unit: str
    geometry: MesanGeometry
    status: int
    headers: Dict[str, str]
    df: pd.DataFrame
    df_info: DataFrame[MesanPointInfoSchema]


class MesanMultiPoint(BaseModel):
    """Multi point model."""

    parameter: str
    parameter_meaning: str
    geo: bool
    downsample: int
    url: str
    approved_time: datetime
    reference_time: datetime
    valid_time: datetime
    status: int
    headers: Dict[str, str]
    df: DataFrame[MesanMultiPointSchema]
