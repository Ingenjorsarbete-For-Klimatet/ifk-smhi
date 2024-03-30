"""SMHI Metfcts API module."""

from typing import Dict

from smhi.constants import METFCTS_PARAMETER_DESCRIPTIONS, METFCTS_URL
from smhi.mesan import Mesan
from smhi.models.metfcts_model import (
    MetfctsApprovedTime,
    MetfctsMultiPointData,
    MetfctsParameters,
    MetfctsPointData,
    MetfctsPolygon,
    MetfctsValidTime,
)
from smhi.models.variable_model import (
    ApprovedTime,
    MultiPointData,
    Parameters,
    PointData,
    Polygon,
    ValidTime,
)


class Metfcts(Mesan):
    """SMHI Metfcts module."""

    __parameters_model: Parameters = MetfctsParameters
    __approved_time_model: ApprovedTime = MetfctsApprovedTime
    __valid_time_model: ValidTime = MetfctsValidTime
    __polygon_model: Polygon = MetfctsPolygon
    __point_data_model: PointData = MetfctsPointData
    __multipoint_data_model: MultiPointData = MetfctsMultiPointData

    _category: str = "pmp3g"
    _version: int = 2
    _base_url: str = METFCTS_URL
    _parameter_descriptions: Dict[str, str] = METFCTS_PARAMETER_DESCRIPTIONS
