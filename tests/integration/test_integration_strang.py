"""Strang integration tests."""

import time

import pandas as pd
import pytest
from smhi.strang import Strang


def get_point(file=None):
    return (
        "date_time" if file is None else pd.read_csv(file, parse_dates=[0], index_col=0)
    )


@pytest.fixture
def get_multipoint():
    df = pd.read_csv(
        "tests/fixtures/strang/strang_result_multipoint_2020_01_01_monthly_10.csv",
        index_col=0,
    )

    return df


class TestIntegrationStrang:
    """Integration tests for Strang class."""

    @pytest.mark.parametrize(
        "lat, lon, parameter, time_from, time_to, time_interval, expected_result",
        [
            (
                58,
                16,
                118,
                "2020-01-01",
                "2020-01-02",
                "hourly",
                get_point(
                    "tests/fixtures/strang/strang_result_hourly_2020_01_01_2020_01_02.csv"
                ),
            ),
            (
                58,
                16,
                118,
                "2020-01-01",
                "2020-01-02",
                "daily",
                get_point(
                    "tests/fixtures/strang/strang_result_daily_2020_01_01_2020_01_02.csv"
                ),
            ),
            (
                58,
                16,
                118,
                "2020-01-01",
                "2020-02-01",
                "monthly",
                get_point(
                    "tests/fixtures/strang/strang_result_monthly_2020_01_01_2020_02_01.csv"
                ),
            ),
            (58, 16, 118, None, None, None, get_point()),
        ],
    )
    def test_integration_strang_point(
        self, lat, lon, parameter, time_from, time_to, time_interval, expected_result
    ):
        """Strang Point class integration tests.

        These tests require internet connectivity.
        """
        client = Strang()
        point_model = client.get_point(
            lat, lon, parameter, time_from, time_to, time_interval
        )

        assert point_model.parameter_key == parameter
        assert (
            point_model.parameter_meaning
            == client._available_parameters[parameter].meaning
        )
        assert point_model.latitude == lat
        assert point_model.longitude == lon
        assert point_model.time_interval == time_interval
        assert point_model.status == 200

        if time_from is not None:
            pd.testing.assert_frame_equal(expected_result, point_model.df)
        else:
            assert expected_result == point_model.df.index.name

        time.sleep(1)

    def test_integration_strang_multipoint(self, get_multipoint):
        """Strang MultiPoint integration tests.

        These tests require internet connectivity.
        """
        client = Strang()
        parameter = 116
        valid_time = "2020-01-01"
        time_interval = "monthly"
        multipoint_model = client.get_multipoint(parameter, valid_time, time_interval)

        assert multipoint_model.parameter_key == parameter
        assert (
            multipoint_model.parameter_meaning
            == client._available_parameters[parameter].meaning
        )
        assert multipoint_model.time_interval == time_interval
        assert multipoint_model.status == 200

        pd.testing.assert_frame_equal(
            get_multipoint,
            multipoint_model.df.iloc[:10, :],
        )

        time.sleep(1)
