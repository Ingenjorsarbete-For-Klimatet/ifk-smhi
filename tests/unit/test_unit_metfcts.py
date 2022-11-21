"""SMHI Metfcts v1 unit tests."""
import json
import arrow
import pytest
from smhi.metfcts import Metfcts
from unittest.mock import patch


BASE_URL = (
    "https://opendata-download-metfcst.smhi.se/" + "api/category/pmp3g/version/2/"
)


class TestUnitMetfcts:
    """Unit tests for Metfcts class."""

    def test_unit_metfcts_init(self):
        """Unit test for Metfcts init method."""
        client = Metfcts()

        assert client._category == "pmp3g"
        assert client._version == 2
        assert client.latitude is None
        assert client.longitude is None
        assert client.status is None
        assert client.header is None
        assert client.data is None
        assert client.base_url == BASE_URL
        assert client.url is None
