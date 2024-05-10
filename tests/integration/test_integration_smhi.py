"""SMHI integration tests."""

from unittest.mock import patch

import pandas as pd
import pytest
from smhi.smhi import SMHI


class MockMetobsStationLink:
    """Support class to mock MetObs StationLink object."""

    def __init__(self, id: int, name: str, lat: float, lon: float):
        """Initiate parameters."""
        self.id = id
        self.name = name
        self.latitude = lat
        self.longitude = lon


class MockParameterModel:
    """Support class to mock Metobs Parameter object."""

    def __init__(self, station: MockMetobsStationLink):
        """Initiate station."""
        self.station = station


class MockDataModel:
    """Support class to mock Metobs Data object."""

    def __init__(self, station: MockMetobsStationLink, parameter: MockParameterModel):
        """initiate data."""
        df = pd.DataFrame(
            {
                "Lufttemperatur": [19.0, 18.2, 15.3, 17.0, 18.8],
                "Kvalitet": ["G", "G", "G", "G", "G"],
            },
            index=pd.to_datetime(
                [
                    "1859-08-01 07:00:00+00:00",
                    "1859-08-01 13:00:00+00:00",
                    "1859-08-01 20:00:00+00:00",
                    "1859-08-02 07:00:00+00:00",
                    "1859-08-02 13:00:00+00:00",
                ],
            ),
        )
        self.df = df


class TestIntegrationSMHI:
    """Integration test of SMHI class."""

    @pytest.mark.parametrize(
        "parameter, city, period,radius,expected_result",
        [
            (
                1,
                "Göteborg",
                None,
                None,
                "Result",
            ),
        ],
    )
    @patch(
        "smhi.metobs.Stations.__new__",
        return_value=MockParameterModel([MockMetobsStationLink(1, "Göteborg", 16, 57)]),
    )
    @patch("smhi.metobs.Periods.__new__")
    @patch(
        "smhi.metobs.Data.__new__",
        return_value=MockDataModel(
            MockMetobsStationLink(1, "Göteborg", 16, 57),
            MockParameterModel(MockMetobsStationLink(1, "Göteborg", 16, 57)),
        ),
    )
    def test_integration_smhi(
        self,
        mock_data,
        mock_periods,
        mock_stations,
        parameter,
        city,
        period,
        radius,
        expected_result,
    ):
        """Integration test of SMHI class."""

        client = SMHI()
        data = client.get_data_by_city(parameter, city)
        assert len(data.df["Lufttemperatur"]) == 5
