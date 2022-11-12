"""
SMHI Mesan v1 unit tests.
"""
import pytest
from smhi.mesan import Mesan
from unittest.mock import patch


BASE_URL = (
    "https://opendata-download-metanalys.smhi.se/" + "api/category/mesan1g/version/2/"
)


class TestUnitMesan:
    """
    Unit tests for Mesan class.
    """

    def test_unit_mesan_init(self):
        """
        Unit test for Mesan init method.
        """
        client = Mesan()

        assert client._category == "mesan1g"
        assert client._version == 2
        assert client.latitude is None
        assert client.longitude is None
        assert client.status is None
        assert client.header is None
        assert client.data is None
        assert client.base_url == BASE_URL
        assert client.url is None

    @patch("smhi.mesan.Mesan._get_data", return_value=(None, None, None))
    def test_unit_mesan_approved_time(self, mock_get_data):
        """
        Unit test for Mesan approved_time property.

        Args:
            mock_get_data: mock _get_data method
        """
        client = Mesan()
        client.approved_time
        mock_get_data.assert_called_once_with(BASE_URL + "approvedtime.json")

    @patch("smhi.mesan.Mesan._get_data", return_value=(None, None, None))
    def test_unit_mesan_valid_time(self, mock_get_data):
        """
        Unit test for Mesan valid_time property.

        Args:
            mock_get_data: mock _get_data method
        """
        client = Mesan()
        client.valid_time
        mock_get_data.assert_called_once_with(BASE_URL + "validtime.json")

    @patch("smhi.mesan.Mesan._get_data", return_value=(None, None, None))
    def test_unit_mesan_geo_polygon(self, mock_get_data):
        """
        Unit test for Mesan geo_polygon property.

        Args:
            mock_get_data: mock _get_data method
        """
        client = Mesan()
        client.geo_polygon
        mock_get_data.assert_called_once_with(BASE_URL + "geotype/polygon.json")

    @pytest.mark.parametrize("downsample", [(0), (20)])
    @patch("smhi.mesan.Mesan._get_data", return_value=(None, None, None))
    def test_unit_mesan_get_geo_multipoint(self, mock_get_data, downsample):
        """
        Unit test for Mesan geo_multipoint property.

        Args:
            mock_get_data: mock _get_data method
            downsample: downsample parameter
        """
        client = Mesan()
        client.get_geo_multipoint(downsample)
        mock_get_data.assert_called_once_with(
            BASE_URL
            + "geotype/multipoint.json?downsample={downsample}".format(
                downsample=downsample
            )
        )

    @patch("smhi.mesan.Mesan._get_data", return_value=(None, None, None))
    def test_unit_mesan_parameters(self, mock_get_data):
        """
        Unit test for Mesan parameters property.

        Args:
            mock_get_data: mock _get_data method
        """
        client = Mesan()
        client.parameters
        mock_get_data.assert_called_once_with(BASE_URL + "parameter.json")
