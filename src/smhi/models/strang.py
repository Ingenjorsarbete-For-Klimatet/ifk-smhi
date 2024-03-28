from __future__ import annotations

from datetime import datetime
from typing import Callable, Dict, Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict


class StrangParameter(BaseModel):
    parameter: Optional[int]
    meaning: Optional[str]
    time_from: Optional[datetime]
    time_to: Callable


class StrangMultiPointItem(BaseModel):
    lat: float
    lon: float
    value: float


class StrangMultiPoint(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    parameter: StrangParameter
    valid_time: Optional[str] = None
    time_interval: Optional[str] = None
    url: str
    status: bool
    headers: Dict[str, str]
    data: pd.DataFrame


class StrangPointItem(BaseModel):
    date_time: str
    value: float


class StrangPoint(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    longitude: float
    latitude: float
    parameter: StrangParameter
    time_from: Optional[str] = None
    time_to: Optional[str] = None
    time_interval: Optional[str] = None
    url: str
    status: bool
    headers: Dict[str, str]
    data: pd.DataFrame
