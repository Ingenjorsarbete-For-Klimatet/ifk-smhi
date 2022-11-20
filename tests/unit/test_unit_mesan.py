"""
SMHI Mesan v1 unit tests.
"""
import json
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

    @pytest.mark.parametrize("downsample", [(0), (2), (20), (21)])
    @patch("smhi.mesan.Mesan._get_data", return_value=(None, None, None))
    def test_unit_mesan_get_geo_multipoint(self, mock_get_data, downsample):
        """
        Unit test for Mesan get_geo_multipoint method.

        Args:
            mock_get_data: mock _get_data method
            downsample: downsample parameter
        """
        client = Mesan()
        client.get_geo_multipoint(downsample)
        if downsample < 1:
            mock_get_data.assert_called_once_with(BASE_URL + "geotype/multipoint.json")
        elif downsample > 20:
            mock_get_data.assert_called_once_with(
                BASE_URL + "geotype/multipoint.json?downsample=20"
            )
        else:
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

    @pytest.mark.parametrize("lat, lon", [(0, 0), (1, 1)])
    @patch("smhi.mesan.Mesan._get_data", return_value=(None, None, None))
    def test_unit_mesan_get_point(self, mock_get_data, lat, lon):
        """
        Unit test for Mesan get_point method.

        Args:
            mock_get_data: mock _get_data method
            lat: latitude
            lon: longitude
        """
        client = Mesan()
        client.get_point(lat, lon)
        mock_get_data.assert_called_once_with(
            BASE_URL
            + "geotype/point/lon/{longitude}/lat/{latitude}/data.json".format(
                longitude=lon, latitude=lat
            )
        )

    @pytest.mark.parametrize(
        "validtime, parameter, leveltype, level, downsample", [(0, 0, 0, 0, 0)]
    )
    @patch("smhi.mesan.Mesan._get_data", return_value=(None, None, None))
    def test_unit_mesan_get_multipoint(
        self, mock_get_data, validtime, parameter, leveltype, level, downsample
    ):
        """
        Unit test for Mesan get_multipoint method.

        Args:
            mock_get_data: mock _get_data method
            validtime: valid time,
            parameter: parameter,
            leveltype: level type,
            level: level,
            downsample: downsample,
        """
        client = Mesan()
        client.get_multipoint(validtime, parameter, leveltype, level, downsample)
        mock_get_data.assert_called_once_with(
            BASE_URL
            + "geotype/multipoint/"
            + "validtime/{YYMMDDThhmmssZ}/parameter/{p}/leveltype/".format(
                YYMMDDThhmmssZ=validtime,
                p=parameter,
            )
            + "{lt}/level/{l}/data.json?with-geo=false&downsample={downsample}".format(
                lt=leveltype,
                l=level,
                downsample=downsample,
            )
        )

    @pytest.mark.parametrize(
        "response",
        [
            (
                type(
                    "ResponseClass",
                    (object,),
                    {"ok": False, "headers": None, "content": None},
                )()
            ),
            (
                type(
                    "ResponseClass",
                    (object,),
                    {"ok": True, "headers": "header", "content": r"""{"data": 1}"""},
                )()
            ),
        ],
    )
    @patch("smhi.mesan.json.loads")
    @patch("smhi.mesan.requests.get")
    def test_unit_mesan_get_data(self, mock_get, mock_loads, response):
        """
        Unit test for Mesan _get_data method.

        Args:
            mock_get: mock requests get method
            mock_loads: mock json loads method
            response: response object
        """
        client = Mesan()
        mock_get.return_value = response
        status, headers, data = client._get_data("url")

        mock_get.assert_called_once_with("url")
        assert status is response.ok
        assert headers == response.headers
        if status:
            assert data == json.loads(response.content)
        else:
            assert data is None
