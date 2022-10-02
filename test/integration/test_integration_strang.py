"""
STRÅNG integration tests.
"""
import pytest
import datetime
from dateutil.tz import tzutc
from smhi.strang import StrangPoint


RESULT_HOURLY_2020_01_01_2020_01_02 = [
    {"date_time": datetime.datetime(2020, 1, 1, 0, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 1, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 2, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 3, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 4, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 5, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 6, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 7, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 8, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 9, 0, tzinfo=tzutc()), "value": 60.4},
    {"date_time": datetime.datetime(2020, 1, 1, 10, 0, tzinfo=tzutc()), "value": 206.5},
    {"date_time": datetime.datetime(2020, 1, 1, 11, 0, tzinfo=tzutc()), "value": 109.0},
    {"date_time": datetime.datetime(2020, 1, 1, 12, 0, tzinfo=tzutc()), "value": 49.7},
    {"date_time": datetime.datetime(2020, 1, 1, 13, 0, tzinfo=tzutc()), "value": 182.4},
    {"date_time": datetime.datetime(2020, 1, 1, 14, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 15, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 16, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 17, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 18, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 19, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 20, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 21, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 22, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 1, 23, 0, tzinfo=tzutc()), "value": 0.0},
    {"date_time": datetime.datetime(2020, 1, 2, 0, 0, tzinfo=tzutc()), "value": 0.0},
]

RESULT_DAILY_2020_01_01_2020_01_02 = [
    {"date_time": datetime.datetime(2020, 1, 1, 0, 0, tzinfo=tzutc()), "value": 608.0},
    {"date_time": datetime.datetime(2020, 1, 2, 0, 0, tzinfo=tzutc()), "value": 12.1},
]

RESULT_MONTHLY_2020_01_01_2020_02_01 = [
    {
        "date_time": datetime.datetime(2020, 1, 1, 0, 0, tzinfo=tzutc()),
        "value": 23086.5,
    },
    {
        "date_time": datetime.datetime(2020, 2, 1, 0, 0, tzinfo=tzutc()),
        "value": 51961.8,
    },
]


class TestIntegrationStrangPoint:
    """
    Integration tests for STRÅNG Point class.
    """

    @pytest.mark.parametrize(
        "lon, lat, parameter, time_from, time_to, time_interval, expected_result",
        [
            (
                16,
                58,
                118,
                "2020-01-01",
                "2020-01-02",
                "hourly",
                RESULT_HOURLY_2020_01_01_2020_01_02,
            ),
            (
                16,
                58,
                118,
                "2020-01-01",
                "2020-01-02",
                "daily",
                RESULT_DAILY_2020_01_01_2020_01_02,
            ),
            (
                16,
                58,
                118,
                "2020-01-01",
                "2020-02-01",
                "monthly",
                RESULT_MONTHLY_2020_01_01_2020_02_01,
            ),
            (
                16,
                58,
                118,
                None,
                None,
                None,
                "date_time",
            ),
        ],
    )
    def test_integration_strang(
        self, lon, lat, parameter, time_from, time_to, time_interval, expected_result
    ):
        """
        STRÅNG Point class integration tests. These tests require internet connectivity.

        Args:
            lon: latitude
            lat: longitude
            parameter: parameter
            time_from: from
            time_to: to
            time_interval: interval
            expected_result: expected result
        """
        client = StrangPoint()
        client.fetch_data(lon, lat, parameter, time_from, time_to, time_interval)

        if time_from is not None:
            assert client.data == expected_result
        else:
            assert expected_result in client.data[0]
