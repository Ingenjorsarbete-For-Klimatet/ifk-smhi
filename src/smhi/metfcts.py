"""SMHI Metfcts API module."""

from typing import Dict

import arrow
from smhi.constants import METFCTS_PARAMETER_DESCRIPTIONS, METFCTS_URL
from smhi.mesan import Mesan
from smhi.models.metfcts_model import (
    MetfctsApprovedTime,
    MetfctsGeoMultiPoint,
    MetfctsGeoPolygon,
    MetfctsMultiPointModel,
    MetfctsParameter,
    MetfctsPointModel,
    MetfctsValidTime,
)
from smhi.models.variable_model import (
    ApprovedTime,
    GeoMultiPoint,
    GeoPolygon,
    MultiPointModel,
    Parameter,
    PointModel,
    ValidTime,
)


class Metfcts(Mesan):
    """SMHI Metfcts module."""

    __parameters_model: Parameter = MetfctsParameter
    __approved_time_model: ApprovedTime = MetfctsApprovedTime
    __valid_time_model: ValidTime = MetfctsValidTime
    __geo_polygon_model: GeoPolygon = MetfctsGeoPolygon
    __geo_multipoint_model: GeoMultiPoint = MetfctsGeoMultiPoint
    __point_data_model: PointModel = MetfctsPointModel
    __multipoint_data_model: MultiPointModel = MetfctsMultiPointModel

    _category: str = "pmp3g"
    _version: int = 2
    _base_url: str = METFCTS_URL
    _parameter_descriptions: Dict[str, str] = METFCTS_PARAMETER_DESCRIPTIONS

    def _check_valid_time(self, test_time: str) -> bool:
        """Check if time is valid, that is within a day window.

        This might be overly restrictive but avoids an extra API call for each get_multipoint.

        Args:
            test_time: time to check

        Returns
            true if valid and false if not valid
        """
        valid_time = self._format_datetime(test_time)
        return -1 < (arrow.get(valid_time) - arrow.now("Z").shift(hours=-1)).days < 10
