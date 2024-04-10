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
    """Strang parameter model."""

    key: Optional[int]
    meaning: Optional[str]
    time_from: Optional[datetime] = None
    time_to: Optional[Callable]


class StrangPointItem(BaseModel):
    date_time: datetime
    value: float


class StrangMultiPointItem(BaseModel):
    lat: float
    lon: float
    value: float


class StrangPoint(BaseModel):
    """Point model."""

    parameter_key: int
    parameter_meaning: str
    longitude: float
    latitude: float
    time_from: Optional[datetime]
    time_to: Optional[datetime]
    time_interval: Optional[str]
    url: str
    status: int
    headers: Dict[str, str]
    df: Optional[DataFrame[StrangPointSchema]]


class StrangMultiPoint(BaseModel):
    """Multi point model."""

    parameter_key: int
    parameter_meaning: str
    valid_time: Optional[datetime]
    time_interval: Optional[str]
    url: str
    status: int
    headers: Dict[str, str]
    df: Optional[DataFrame[StrangMultiPointSchema]]
