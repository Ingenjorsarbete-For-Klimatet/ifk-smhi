from __future__ import annotations

from datetime import datetime
from typing import Annotated, Callable, Dict, Optional

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Index, Series
from pydantic import BaseModel


class StrangPointSchema(pa.DataFrameModel):
    date_time: Index[Annotated[pd.DatetimeTZDtype, "ns", "UTC"]] = pa.Field(
        check_name=True, unique=True
    )
    value: Series[float]


class StrangMultiPointSchema(pa.DataFrameModel):
    lat: Series[float]
    lon: Series[float]
    value: Series[float]


class StrangParameter(BaseModel):
    key: Optional[int]
    meaning: Optional[str]
    time_from: Optional[datetime]
    time_to: Callable


class StrangMultiPointItem(BaseModel):
    lat: float
    lon: float
    value: float


class StrangMultiPoint(BaseModel):
    parameter_key: int
    parameter_meaning: str
    valid_time: Optional[str] = None
    time_interval: Optional[str] = None
    url: str
    status: int
    headers: Dict[str, str]
    data: DataFrame[StrangMultiPointSchema]


class StrangPointItem(BaseModel):
    date_time: str
    value: float


class StrangPoint(BaseModel):
    parameter_key: int
    parameter_meaning: str
    longitude: float
    latitude: float
    time_from: Optional[str] = None
    time_to: Optional[str] = None
    time_interval: Optional[str] = None
    url: str
    status: int
    headers: Dict[str, str]
    data: DataFrame[StrangPointSchema]
