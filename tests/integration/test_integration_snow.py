"""Snow integration tests."""

import time

import arrow
import pytest
from smhi.constants import SNOW_PARAMETER_DESCRIPTIONS
from smhi.snow import Snow

GEO_POLYGON_TYPE = "Polygon"
GEO_MULTIPOINT_TYPE = "MultiPoint"
NUM_GEO_COORDINATES = 10
NUM_PARAMETERS = 10
NUM_VALID_TIME = 24
MIN_TEMPERATURE = -1000


def datetime_between_day(test_time):
    ttime = arrow.get(test_time)
    return ttime.shift(days=-1) < ttime < ttime.shift(days=1)


def datetime_between_week_and_a_half(test_time):
    ttime = arrow.get(test_time)
    return arrow.utcnow().shift(hours=-2) < ttime < arrow.utcnow().shift(days=11)


class TestIntegrationSnow:
    """Integration tests for Snow class."""

    def test_integration_snow_created_time(self):
        """Integration test for created time property."""
        client = Snow()
        created_time = client.created_time.created_time
        assert datetime_between_day(created_time)

        time.sleep(1)

    def test_integration_snow_parameters(self):
        """Integration test for parameters property."""
        client = Snow()
        parameters = client.parameters

        for parameter in parameters.parameter:
            assert (
                parameter.name in SNOW_PARAMETER_DESCRIPTIONS
            ), f"Parameter '{parameter.name}' not found in SNOW_PARAMETER_DESCRIPTIONS"
        assert len(parameters.parameter) > NUM_PARAMETERS

        time.sleep(1)

    def test_integration_snow_times(self):
        """Integration test for times property."""
        client = Snow()
        times = client.times.times
        for test_time in times:
            assert datetime_between_week_and_a_half(test_time)

        assert len(times) > NUM_VALID_TIME

        time.sleep(1)

    def test_integration_snow_geo_polygon(self):
        """Integration test for geo_polygon property."""
        client = Snow()
        geo_polygon = client.geo_polygon
        assert geo_polygon.type_ == GEO_POLYGON_TYPE
        assert len(geo_polygon.coordinates[0]) > NUM_GEO_COORDINATES

        time.sleep(1)

    @pytest.mark.parametrize("downsample", [(1)])
    def test_integration_snow_get_geo_multipoint(self, downsample):
        """Integration test for get_geo_multipoint method."""
        client = Snow()
        geo_multipoint = client.get_geo_multipoint(downsample)
        assert geo_multipoint.type_ == GEO_MULTIPOINT_TYPE
        assert len(geo_multipoint.coordinates) > NUM_GEO_COORDINATES

        time.sleep(1)

    @pytest.mark.parametrize("lat, lon", [(58, 16)])
    def test_integration_snow_get_point(self, lat, lon):
        """Integration test for get_point method."""
        client = Snow()
        point = client.get_point(lat, lon)

        assert not point.df.empty
        assert (point.df != 0).any().any()

        time.sleep(1)

    @pytest.mark.parametrize(
        "time_, parameter, geo, downsample",
        [
            (
                arrow.utcnow().shift(hours=3).format("YYYYMMDDTHH"),
                "air_temperature",
                False,
                10,
            ),
            (
                arrow.utcnow().shift(hours=3).format("YYYYMMDDTHH"),
                "air_temperature",
                True,
                10,
            ),
        ],
    )
    def test_integration_snow_get_multipoint(self, time_, parameter, geo, downsample):
        """Integration test for get_multipoint method."""
        client = Snow()
        multipoint = client.get_multipoint(time_, parameter, geo, downsample)

        assert not multipoint.df.empty
        assert multipoint.df["value"].iloc[0] > MIN_TEMPERATURE

        if geo:
            assert multipoint.df["lon"].iloc[0] > 0
            assert multipoint.df["lat"].iloc[0] > 0

        time.sleep(1)
