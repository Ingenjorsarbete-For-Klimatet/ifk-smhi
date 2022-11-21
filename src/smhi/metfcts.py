"""SMHI Metfcts API module."""
from smhi.mesan import Mesan
from smhi.constants import METFCTS_URL


class Metfcts(Mesan):
    """SMHI Metfcts module."""

    def __init__(self) -> None:
        """Initialise Metfcts."""
        self._category = "pmp3g"
        self._version = 2

        self.latitude = None
        self.longitude = None
        self.status = None
        self.header = None
        self.data = None
        self.base_url = METFCTS_URL.format(
            category=self._category, version=self._version
        )
        self.url = None
