"""
SMHI unit tests.
"""
from unittest.mock import patch
from smhi.strang import Strang
from functools import partial
from smhi.constants import (
    STRANG,
    STRANG_URL,
    STRANG_URL_TIME,
    STRANG_PARAMETERS,
    STRANG_DATE_FORMAT,
    STRANG_DATETIME_FORMAT,
    STRANG_TIME_INTERVALS,
)


CATEGORY = "strang1g"
VERSION = 1


class TestUnitStrang:
    """
    Unit tests for STRÅNG class.
    """

    def test_unit_strang_init(self):
        """
        Unit test for STRÅNG init method.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
        """
        client = Strang()

        assert client._category == CATEGORY
        assert client._version == VERSION

        assert client.latitude is None
        assert client.longitude is None
        assert client.parameter is None
        assert client.status is None
        assert client.header is None
        assert client.data is None

        assert (
            all(
                [x == y for x, y in zip(client.available_parameters, STRANG_PARAMETERS)]
            )
            is True
        )

        raw_url_dict = {"category": CATEGORY, "version": VERSION}
        for k1, k2 in zip(
            sorted(raw_url_dict.keys()), sorted(client.raw_url.keywords.keys())
        ):
            assert k1 == k2
            assert raw_url_dict[k1] == client.raw_url.keywords[k2]

        assert client.time_url is STRANG_URL_TIME
        assert client.url is None

    def test_unit_strang_parameters(self):
        """
        Unit test for STRÅNG parameters get property.
        """
        client = Strang()
        assert (
            all(
                [x == y for x, y in zip(client.available_parameters, STRANG_PARAMETERS)]
            )
            is True
        )

    @patch("smhi.strang.check_date_validity")
    @patch("smhi.strang.fetch_and_load_strang_data")
    def test_unit_strang_fetch_data(
        self, mock_check_date_validity, mock_fetch_and_load_strang_data
    ):
        """
        Unit test for STRÅNG fetch_data method.

        Args:
            mock_check_date_validity: mock check_date_validity method
            mock_fetch_and_load_strang_data: mock fetch_and_load_strang_data method
        """
        client = Strang()
        pass

    def test_unit_strang_check_date_validity(self):
        """
        Unit test for STRANG check_date_validity function.
        """
        pass

    @patch("smhi.strang.requests.get")
    @patch("smhi.strang.json.loads")
    def test_unit_strang_fetch_and_load_strang_data(
        self, mock_requests_get, mock_json_loads
    ):
        """
        Unit test for STRANG fetch_and_load_strang_data function.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
        """
        pass
