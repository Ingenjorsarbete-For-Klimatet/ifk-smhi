from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Index, Series
from pydantic import BaseModel, ConfigDict, Field


class MetfctsValidTime(BaseModel):
    url: str
    status: int
    headers: Dict[str, str]
    valid_time: List[str]


class MetfctsApprovedTime(BaseModel):
    url: str
    status: int
    headers: Dict[str, str]
    approved_time: datetime
    reference_time: datetime


class MetfctsGeoPolygon(BaseModel):
    url: str
    status: int
    headers: Dict[str, str]
    type_: str = Field(..., alias="type")
    coordinates: List[List[List[float]]]


class MetfctsGeoMultiPoint(BaseModel):
    url: str
    status: int
    headers: Dict[str, str]
    type_: str = Field(..., alias="type")
    coordinates: List[List[float]]


class MetfctsParameterItem(BaseModel):
    name: str
    key: str
    level_type: str = Field(..., alias="levelType")
    level: int
    unit: str
    missing_value: int = Field(..., alias="missingValue")


class MetfctsParameter(BaseModel):
    url: str
    status: int
    headers: Dict[str, str]
    parameter: List[MetfctsParameterItem]


class MetfctsPointInfoSchema(pa.DataFrameModel):
    name: Index[str] = pa.Field(check_name=True, unique=True)
    level: Series[int]
    level_type: Series[str]
    unit: Series[str]


class MetfctsMultiPointSchema(pa.DataFrameModel):
    lat: Optional[Series[float]]
    lon: Optional[Series[float]]
    value: Series[float]


class MetfctsPoint(BaseModel):
    """Point model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    longitude: float
    latitude: float
    url: str
    approved_time: datetime
    reference_time: datetime
    level_unit: str
    geometry: MetfctsGeoPolygon
    status: int
    headers: Dict[str, str]
    df: pd.DataFrame
    df_info: DataFrame[MetfctsPointInfoSchema]


class MetfctsMultiPoint(BaseModel):
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
    df: DataFrame[MetfctsMultiPointSchema]
