"""SMHI Metfcts API module."""

from smhi.constants import METFCTS_PARAMETER_DESCRIPTIONS, METFCTS_URL
from smhi.mesan import Mesan
from smhi.models.metfcts import (
    MetfctsApprovedTime,
    MetfctsMultiPointData,
    MetfctsParameters,
    MetfctsPointData,
    MetfctsPolygon,
    MetfctsValidTime,
)


class Metfcts(Mesan):
    """SMHI Metfcts module."""

    __parameters_model = MetfctsParameters
    __approved_time_model = MetfctsApprovedTime
    __valid_time_model = MetfctsValidTime
    __polygon_model = MetfctsPolygon
    __point_data_model = MetfctsPointData
    __multipoint_data_model = MetfctsMultiPointData

    def __init__(self) -> None:
        """Initialise Metfcts."""
        self._category: str = "pmp3g"
        self._version: int = 2
        self._base_url: str = METFCTS_URL.format(
            category=self._category, version=self._version
        )
        self._parameters = self.__parameters_model(*self._get_parameters())
        self._parameter_descriptions = METFCTS_PARAMETER_DESCRIPTIONS
