"""Mesan integration tests."""
import json
import arrow
import pytest
import requests
from smhi.mesan import Mesan

BASE_URL = "https://opendata-download-metanalys.smhi.se"
APPROVED_TIME = BASE_URL + "/api/category/mesan1g/version/2/approvedtime.json"
VALID_TIME = BASE_URL + "/api/category/mesan1g/version/2/validtime.json"
GEO_POLYGON = BASE_URL + "/api/category/mesan1g/version/2/geotype/polygon.json"
MULTIPOINT_D0 = BASE_URL + "/api/category/mesan1g/version/2/geotype/multipoint.json"
MULTIPOINT_D1 = (
    BASE_URL + "/api/category/mesan1g/version/2/geotype/multipoint.json?downsample=1"
)
MULTIPOINT_D2 = (
    BASE_URL + "/api/category/mesan1g/version/2/geotype/multipoint.json?downsample=2"
)
MULTIPOINT_D10 = (
    BASE_URL + "/api/category/mesan1g/version/2/geotype/multipoint.json?downsample=10"
)
MULTIPOINT_D20 = (
    BASE_URL + "/api/category/mesan1g/version/2/geotype/multipoint.json?downsample=20"
)
PARAMETERS = BASE_URL + "/api/category/mesan1g/version/2/parameter.json"

APPROVED_TIME_NOW = json.loads(requests.get(APPROVED_TIME).content)
VALID_TIME_NOW = json.loads(requests.get(VALID_TIME).content)
GEO_POLYGON_NOW = json.loads(requests.get(GEO_POLYGON).content)
MULTIPOINT_D0_NOW = json.loads(requests.get(MULTIPOINT_D0).content)
MULTIPOINT_D1_NOW = json.loads(requests.get(MULTIPOINT_D1).content)
MULTIPOINT_D2_NOW = json.loads(requests.get(MULTIPOINT_D2).content)
MULTIPOINT_D10_NOW = json.loads(requests.get(MULTIPOINT_D10).content)
MULTIPOINT_D20_NOW = json.loads(requests.get(MULTIPOINT_D20).content)
PARAMETERS_NOW = json.loads(requests.get(PARAMETERS).content)


class TestIntegrationMesan:
    """Integration tests for Mesan class."""

    def test_integration_mesan_approved_time(self):
        """Integration test for approved time property."""
        client = Mesan()
        assert client.approved_time == APPROVED_TIME_NOW["approvedTime"]

    def test_integration_mesan_valid_time(self):
        """Integration test for approved time property."""
        client = Mesan()
        assert client.valid_time == VALID_TIME_NOW["validTime"]

    def test_integration_mesan_geo_polygon(self):
        """Integration test for geo_polygon property."""
        client = Mesan()
        assert client.geo_polygon == GEO_POLYGON_NOW["coordinates"]

    @pytest.mark.parametrize(
        "downsample, result",
        [
            (0, MULTIPOINT_D0_NOW),
            (1, MULTIPOINT_D1_NOW),
            (2, MULTIPOINT_D2_NOW),
            (10, MULTIPOINT_D10_NOW),
            (20, MULTIPOINT_D20_NOW),
        ],
    )
    def test_integration_mesan_get_geo_multipoint(self, downsample, result):
        """Integration test for get_geo_multipoint method.

        Args:
            downsample: downsample parameter
            result: expected result
        """
        client = Mesan()
        assert client.get_geo_multipoint(downsample) == result["coordinates"]

    def test_integration_mesan_parameters(self):
        """Integration test for parameters property."""
        client = Mesan()
        assert client.parameters == PARAMETERS_NOW["parameter"]

    @pytest.mark.parametrize("lat, lon", [(58, 16)])
    def test_integration_mesan_get_point(self, lat, lon):
        """Integration test for get_point method.

        Args:
            lat: latitude parameter
            lon: longitude parameter
        """
        url = (
            BASE_URL
            + "/api/category/mesan1g/version/2/geotype/"
            + "point/lon/{longitude}/lat/{latitude}/data.json".format(
                longitude=lon, latitude=lat
            )
        )
        result = json.loads(requests.get(url).content)

        client = Mesan()
        assert client.get_point(lat, lon) == result

    @pytest.mark.parametrize(
        "validtime, parameter, level_type, level, downsample",
        [(VALID_TIME_NOW["validTime"][0], "t", "hl", 2, 2)],
    )
    def test_integration_mesan_get_multipoint(
        self, validtime, parameter, level_type, level, downsample
    ):
        """Integration test for get_multipoint method.

        Args:
            validtime: valid time
            parameter: parameter
            level_type: level type
            level: level
            downsample: downsample
        """
        url = (
            BASE_URL
            + "/api/category/mesan1g/version/2/geotype/"
            + "multipoint/validtime/{YYMMDDThhmmssZ}/".format(
                YYMMDDThhmmssZ=arrow.get(validtime).format("YYYYMMDDThhmmss") + "Z"
            )
            + "parameter/{p}/leveltype/{lt}/level/{l}/".format(
                p=parameter, lt=level_type, l=level
            )
            + "data.json?with-geo=false&downsample={downsample}".format(
                downsample=downsample
            )
        )
        result = json.loads(requests.get(url).content)

        client = Mesan()
        assert (
            client.get_multipoint(validtime, parameter, level_type, level, downsample)
            == result
        )
