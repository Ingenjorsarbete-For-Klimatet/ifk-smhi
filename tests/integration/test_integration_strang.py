"""Strang integration tests."""
import pytest
import pandas as pd
from smhi.strang import Strang


RESULT_HOURLY_2020_01_01_2020_01_02 = pd.read_csv(
    "tests/fixtures/STRANG_RESULT_HOURLY_2020_01_01_2020_01_02.csv",
    parse_dates=[0],
    index_col=0,
)
RESULT_DAILY_2020_01_01_2020_01_02 = pd.read_csv(
    "tests/fixtures/STRANG_RESULT_DAILY_2020_01_01_2020_01_02.csv",
    parse_dates=[0],
    index_col=0,
)
RESULT_MONTHLY_2020_01_01_2020_02_01 = pd.read_csv(
    "tests/fixtures/STRANG_RESULT_MONTHLY_2020_01_01_2020_02_01.csv",
    parse_dates=[0],
    index_col=0,
)
RESULT_MULTIPOINT_2020_01_01_MONTHLY_10 = pd.read_csv(
    "tests/fixtures/STRANG_RESULT_MULTIPOINT_2020_01_01_MONTHLY_10.csv", index_col=0
)


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
                RESULT_HOURLY_2020_01_01_2020_01_02,
            ),
            (
                58,
                16,
                118,
                "2020-01-01",
                "2020-01-02",
                "daily",
                RESULT_DAILY_2020_01_01_2020_01_02,
            ),
            (
                58,
                16,
                118,
                "2020-01-01",
                "2020-02-01",
                "monthly",
                RESULT_MONTHLY_2020_01_01_2020_02_01,
            ),
            (
                58,
                16,
                118,
                None,
                None,
                None,
                "date_time",
            ),
        ],
    )
    def test_integration_strang_point(
        self, lat, lon, parameter, time_from, time_to, time_interval, expected_result
    ):
        """Strang Point class integration tests.

        These tests require internet connectivity.

        Args:
            lat: longitude
            lon: latitude

            parameter: parameter
            time_from: from
            time_to: to
            time_interval: interval
            expected_result: expected result
        """
        client = Strang()
        data = client.get_point(lat, lon, parameter, time_from, time_to, time_interval)

        if time_from is not None:
            pd.testing.assert_frame_equal(expected_result, data)
        else:
            assert expected_result == data.index.name

    def test_integration_strang_multipoint(self):
        """Strang MultiPoint integration tests.

        These tests require internet connectivity.
        """
        client = Strang()
        parameter = 116
        valid_time = "2020-01-01"
        time_interval = "monthly"
        data = client.get_multipoint(parameter, valid_time, time_interval)
        pd.testing.assert_frame_equal(
            RESULT_MULTIPOINT_2020_01_01_MONTHLY_10, data.iloc[:10, :]
        )
