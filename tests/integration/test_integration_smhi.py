"""SMHI integration tests."""

import time

import pytest
from smhi.smhi import SMHI


class TestIntegrationSMHI:
    """Integration test of SMHI class."""

    @pytest.mark.parametrize(
        "parameter, city, period, radius, expected_result",
        [
            (
                1,
                "Göteborg",
                None,
                None,
                ["Lufttemperatur", 72630],
            ),
            (
                5,
                "Göteborg",
                None,
                20,
                ["Nederbördsmängd", 72630],
            ),
        ],
    )
    def test_integration_smhi(
        self,
        parameter,
        city,
        period,
        radius,
        expected_result,
    ):
        """Integration test of SMHI class."""
        client = SMHI()
        data = client.get_data_by_city(parameter, city, radius)
        assert len(data.df[expected_result[0]]) > 0
        assert data.station["Stationsnummer"][0] == expected_result[1]
        time.sleep(1)
