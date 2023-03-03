"""SMHI Mesan v1 unit tests."""
import json
import arrow
import pytest
import pandas as pd
from smhi.mesan import Mesan
from unittest.mock import patch


BASE_URL = (
    "https://opendata-download-metanalys.smhi.se/" + "api/category/mesan1g/version/2/"
)


class TestUnitMesan:
    """Unit tests for Mesan class."""

    def test_unit_mesan_init(self):
        """Unit test for Mesan init method."""
        client = Mesan()

        assert client._category == "mesan1g"
        assert client._version == 2
        assert client.latitude is None
        assert client.longitude is None
        assert client.status is None
        assert client.header is None
        assert client.base_url == BASE_URL
        assert client.url is None

    @patch(
        "smhi.mesan.Mesan._get_data", return_value=({"approvedTime": None}, None, None)
    )
    def test_unit_mesan_approved_time(self, mock_get_data):
        """Unit test for Mesan approved_time property.

        Args:
            mock_get_data: mock _get_data method
        """
        client = Mesan()
        data = client.approved_time
        mock_get_data.assert_called_once_with(BASE_URL + "approvedtime.json")
        assert data == mock_get_data.return_value[0]["approvedTime"]

    @patch("smhi.mesan.Mesan._get_data", return_value=({"validTime": None}, None, None))
    def test_unit_mesan_valid_time(self, mock_get_data):
        """Unit test for Mesan valid_time property.

        Args:
            mock_get_data: mock _get_data method
        """
        client = Mesan()
        data = client.valid_time
        mock_get_data.assert_called_once_with(BASE_URL + "validtime.json")
        assert data == mock_get_data.return_value[0]["validTime"]

    @patch(
        "smhi.mesan.Mesan._get_data",
        return_value=({"type": "Polygon", "coordinates": None}, None, None),
    )
    def test_unit_mesan_geo_polygon(self, mock_get_data):
        """Unit test for Mesan geo_polygon property.

        Args:
            mock_get_data: mock _get_data method
        """
        client = Mesan()
        data = client.geo_polygon
        mock_get_data.assert_called_once_with(BASE_URL + "geotype/polygon.json")
        assert data == mock_get_data.return_value[0]["coordinates"]

    @pytest.mark.parametrize("downsample", [(0), (2), (20), (21)])
    @patch(
        "smhi.mesan.Mesan._get_data",
        return_value=({"type": "MultiPoint", "coordinates": None}, None, None),
    )
    def test_unit_mesan_get_geo_multipoint(self, mock_get_data, downsample):
        """Unit test for Mesan get_geo_multipoint method.

        Args:
            mock_get_data: mock _get_data method
            downsample: downsample parameter
        """
        client = Mesan()
        data = client.get_geo_multipoint(downsample)
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

        assert data == mock_get_data.return_value[0]["coordinates"]

    @patch("smhi.mesan.Mesan._get_data", return_value=({"parameter": None}, None, None))
    def test_unit_mesan_parameters(self, mock_get_data):
        """Unit test for Mesan parameters property.

        Args:
            mock_get_data: mock _get_data method
        """
        client = Mesan()
        data = client.parameters
        mock_get_data.assert_called_once_with(BASE_URL + "parameter.json")
        assert data == mock_get_data.return_value[0]["parameter"]

    @pytest.mark.parametrize("lat, lon", [(0, 0), (1, 1)])
    @patch("smhi.mesan.Mesan._format_data_point", return_value="datatable")
    @patch("smhi.mesan.Mesan._get_data", return_value=({"geometry": None}, None, None))
    def test_unit_mesan_get_point(self, mock_get_data, mock_format_data, lat, lon):
        """Unit test for Mesan get_point method.

        Args:
            mock_get_data: mock _get_data method
            mock_format_data: mock of _format_data
            lat: latitude
            lon: longitude
        """
        client = Mesan()
        data = client.get_point(lat, lon)
        mock_get_data.assert_called_once_with(
            BASE_URL
            + "geotype/point/lon/{longitude}/lat/{latitude}/data.json".format(
                longitude=lon, latitude=lat
            )
        )
        mock_format_data.assert_called_once_with(mock_get_data.return_value[0])
        assert mock_format_data.return_value == data

    @pytest.mark.parametrize(
        "validtime, parameter, leveltype, level, downsample", [(0, 0, 0, 0, 0)]
    )
    @patch("smhi.mesan.Mesan._format_data_multipoint", return_value="data")
    @patch(
        "smhi.mesan.Mesan._get_data",
        return_value=({"approvedTime": "this_time"}, None, None),
    )
    def test_unit_mesan_get_multipoint(
        self,
        mock_get_data,
        mock_format_data_multipoint,
        validtime,
        parameter,
        leveltype,
        level,
        downsample,
    ):
        """Unit test for Mesan get_multipoint method.

        Args:
            mock_get_data: mock _get_data method
            mock_format_data_multipoint: mock _format_data_multipoint method
            validtime: valid time,
            parameter: parameter,
            leveltype: level type,
            level: level,
            downsample: downsample,
        """
        client = Mesan()
        data = client.get_multipoint(validtime, parameter, leveltype, level, downsample)
        validtime = arrow.get(validtime).format("YYYYMMDDThhmmss") + "Z"
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
        mock_format_data_multipoint.assert_called_once_with(
            mock_get_data.return_value[0]
        )
        assert mock_format_data_multipoint.return_value == data

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
        """Unit test for Mesan _get_data method.

        Args:
            mock_get: mock requests get method
            mock_loads: mock json loads method
            response: response object
        """
        client = Mesan()
        mock_get.return_value = response
        data, headers, status = client._get_data("url")

        mock_get.assert_called_once_with("url")
        assert status is response.ok
        assert headers == response.headers
        if status:
            assert data == json.loads(response.content)
        else:
            assert data is None

    def test_unit_mesan_format_data_point(self):
        """Unit test for Mesan _format_data_point."""
        with open("tests/fixtures/unit_mesan_point_format.json") as f:
            input_data = json.load(f)

        result = pd.read_csv(
            "tests/fixtures/unit_mesan_point_format_result.csv",
            parse_dates=[0],
            index_col=0,
            header=[0, 1],
        )

        client = Mesan()
        data = client._format_data_point(input_data)
        pd.testing.assert_frame_equal(result, data)

    def test_unit_mesan_format_data_multipoint(self):
        """Unit test for Mesan _format_data_multipoint."""
        with open("tests/fixtures/unit_mesan_multipoint_format.json") as f:
            input_data = json.load(f)

        result = pd.read_csv(
            "tests/fixtures/unit_mesan_multipoint_format_result.csv",
            parse_dates=[1, 2, 3],
            index_col=0,
        )

        client = Mesan()
        data = client._format_data_multipoint(input_data)
        pd.testing.assert_frame_equal(result, data)
