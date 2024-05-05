"""Mesan integration tests."""

import time

import arrow
import pytest
from smhi.constants import MESAN_PARAMETER_DESCRIPTIONS
from smhi.mesan import Mesan

NUM_VALID_TIME = 24
GEO_POLYGON_TYPE = "Polygon"
GEO_MULTIPOINT_TYPE = "MultiPoint"
NUM_GEO_COORDINATES = 10
NUM_PARAMETERS = 10
MIN_TEMPERATURE = -1000


def datetime_between_day(test_time):
    ttime = arrow.get(test_time)
    return ttime.shift(days=-1) < ttime < ttime.shift(days=1)


def datetime_between_week(test_time):
    ttime = arrow.get(test_time)
    return ttime.shift(days=-2) < ttime < ttime.shift(weeks=2)


class TestIntegrationMesan:
    """Integration tests for Mesan class."""

    def test_integration_mesan_approved_time(self):
        """Integration test for approved time property."""
        client = Mesan()
        approved_time = client.approved_time.approved_time
        assert datetime_between_day(approved_time)

        time.sleep(1)

    def test_integration_mesan_parameters(self):
        """Integration test for parameters property."""
        client = Mesan()
        parameters = client.parameters
        assert all(
            [x.name in MESAN_PARAMETER_DESCRIPTIONS for x in parameters.parameter]
        )
        assert len(parameters.parameter) > NUM_PARAMETERS

        time.sleep(1)

    def test_integration_mesan_valid_time(self):
        """Integration test for approved time property."""
        client = Mesan()
        valid_time = client.valid_time.valid_time
        for test_time in valid_time:
            assert datetime_between_week(test_time)

        assert len(valid_time) == NUM_VALID_TIME

        time.sleep(1)

    def test_integration_mesan_geo_polygon(self):
        """Integration test for geo_polygon property."""
        client = Mesan()
        geo_polygon = client.geo_polygon
        assert geo_polygon.type_ == GEO_POLYGON_TYPE
        assert len(geo_polygon.coordinates[0]) > NUM_GEO_COORDINATES

        time.sleep(1)

    @pytest.mark.parametrize("downsample", [(1)])
    def test_integration_mesan_get_geo_multipoint(self, downsample):
        """Integration test for get_geo_multipoint method."""
        client = Mesan()
        geo_multipoint = client.get_geo_multipoint(downsample)
        assert geo_multipoint.type_ == GEO_MULTIPOINT_TYPE
        assert len(geo_multipoint.coordinates) > NUM_GEO_COORDINATES

        time.sleep(1)

    @pytest.mark.parametrize("lat, lon", [(58, 16)])
    def test_integration_mesan_get_point(self, lat, lon):
        """Integration test for get_point method."""
        client = Mesan()
        point = client.get_point(lat, lon)

        assert not point.df_info.empty
        assert not point.df.empty
        assert point.df["t"].iloc[0] > MIN_TEMPERATURE

        time.sleep(1)

    @pytest.mark.parametrize(
        "validtime, parameter, level_type, level, geo, downsample",
        [
            (
                arrow.utcnow().shift(hours=-1).format("YYYYMMDDTHH"),
                "t",
                "hl",
                2,
                False,
                10,
            )
        ],
    )
    def test_integration_mesan_get_multipoint(
        self, validtime, parameter, level_type, level, geo, downsample
    ):
        """Integration test for get_multipoint method."""
        client = Mesan()
        multipoint = client.get_multipoint(
            validtime, parameter, level_type, level, geo, downsample
        )

        assert not multipoint.df.empty
        assert multipoint.df["value"].iloc[0] > MIN_TEMPERATURE

        time.sleep(1)
