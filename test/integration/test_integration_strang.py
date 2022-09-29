"""
STRÅNG integration tests.
"""
import pytest
from smhi.strang import StrangPoint


class TestIntegrationStrangPoint:
    """
    Integration tests for STRÅNG Point class.
    """

    @pytest.mark.parametrize(
        "lon, lat, parameter, time_from, time_to, time_interval",
        [(0, 0, 116, None, None, None), (0, 0, 0, None, None, None)],
    )
    def test_integration_strang(
        self, lon, lat, parameter, time_from, time_to, time_interval
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
        """
        client = StrangPoint()
        # client.fetch_data(lon, lat, parameter)
