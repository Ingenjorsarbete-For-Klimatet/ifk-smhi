"""SMHI Metfcts API module."""
from smhi.mesan import Mesan
from typing import Any, Optional
from smhi.constants import METFCTS_URL


class Metfcts(Mesan):
    """SMHI Metfcts module."""

    def __init__(self) -> None:
        """Initialise Metfcts."""
        self._category: str = "pmp3g"
        self._version: int = 2

        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.status: Optional[bool] = None
        self.header: Optional[dict[str, str]] = None
        self.data: Optional[dict[str, Any]] = None
        self.base_url: str = METFCTS_URL.format(
            category=self._category, version=self._version
        )
        self.url: Optional[str] = None
