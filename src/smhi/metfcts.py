"""SMHI Metfcts API module."""
from typing import Optional
from smhi.mesan import Mesan
from smhi.constants import METFCTS_URL
from requests.structures import CaseInsensitiveDict


class Metfcts(Mesan):
    """SMHI Metfcts module."""

    def __init__(self) -> None:
        """Initialise Metfcts."""
        self._category: str = "pmp3g"
        self._version: int = 2

        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.status: Optional[bool] = None
        self.header: Optional[CaseInsensitiveDict[str]] = None
        self.base_url: str = METFCTS_URL.format(
            category=self._category, version=self._version
        )
        self.url: Optional[str] = None
