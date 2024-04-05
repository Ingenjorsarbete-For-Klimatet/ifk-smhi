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
    time_to: Optional[Callable]


class StrangPointItem(BaseModel):
    date_time: str
    value: float


class StrangMultiPointItem(BaseModel):
    lat: float
    lon: float
    value: float


class StrangPointModel(BaseModel):
    parameter_key: int
    parameter_meaning: str
    longitude: float
    latitude: float
    time_from: Optional[str]
    time_to: Optional[str]
    time_interval: Optional[str]
    url: str
    status: int
    headers: Dict[str, str]
    df: Optional[DataFrame[StrangPointSchema]]


class StrangMultiPointModel(BaseModel):
    parameter_key: int
    parameter_meaning: str
    valid_time: Optional[str]
    time_interval: Optional[str]
    url: str
    status: int
    headers: Dict[str, str]
    df: Optional[DataFrame[StrangMultiPointSchema]]
