"""
STRÅNG integration tests.
"""
import pytest
import datetime
from dateutil.tz import tzutc
from smhi.strang import Strang


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

RESULT_MULTIPOINT_2020_01_01_MONTHLY_10 = [
    {"lat": 71.139084, "lon": -9.659227, "value": 4.3},
    {"lat": 71.11585, "lon": -9.630623, "value": 4.3},
    {"lat": 71.09262, "lon": -9.602085, "value": 4.5},
    {"lat": 71.1481, "lon": -9.589094, "value": 4.3},
    {"lat": 71.06939, "lon": -9.573616, "value": 4.6},
    {"lat": 71.12487, "lon": -9.560553, "value": 4.3},
    {"lat": 71.04615, "lon": -9.545213, "value": 4.7},
    {"lat": 71.10162, "lon": -9.532079, "value": 4.5},
    {"lat": 71.157104, "lon": -9.5189, "value": 4.3},
    {"lat": 71.0229, "lon": -9.516877, "value": 5.1},
]


class TestIntegrationStrang:
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
    def test_integration_strang_point(
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
        client = Strang()
        client.get_point(lon, lat, parameter, time_from, time_to, time_interval)

        if time_from is not None:
            assert client.data == expected_result
        else:
            assert expected_result in client.data[0]

    def test_integration_strang_multipoint(self):
        """
        STRÅNG MultiPoint class integration tests. These tests require internet connectivity.
        """
        client = Strang()
        parameter = 116
        valid_time = "2020-01-01"
        date_interval = "monthly"
        client.get_multipoint(parameter, valid_time, date_interval)

        lon_sorted_data = sorted(client.data, key=lambda x: x["lon"])[:10]

        assert RESULT_MULTIPOINT_2020_01_01_MONTHLY_10 == lon_sorted_data
