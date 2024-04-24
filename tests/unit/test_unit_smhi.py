"""SMHI unit tests."""

from unittest.mock import MagicMock, patch
import pytest
from smhi.smhi import SMHI
import pandas as pd


class TestUnitSMHI:
    """Unit tests for SMHI class."""

    @patch("smhi.metobs.Parameters.__new__")
    def test_unit_smhi_init(self, mock_parameters):
        """Unit test for SMHI init method.

        Args:
            mock_requests_metobs: mock requests metobs object
        """
        client = SMHI()

        assert client.parameters

    @pytest.mark.parametrize("parameter", [(None), (1)])
    @patch("smhi.metobs.Stations.__new__")
    def test_unit_smhi_get_stations(self, mock_station_data, parameter):
        """Unit test for SMHI get_stations method.

        Args:
            parameter: parameter (int)
        """
        client = SMHI()
        assert client.get_stations(parameter)

    @pytest.mark.parametrize("parameter_title", [(None), ("Snöfall")])
    @patch("smhi.metobs.Stations.__new__")
    def test_unit_smhi_get_stations_from_title(
        self, mock_station_data, parameter_title
    ):
        """Unit test for SMHI get_stations_from_title method.

        Args:
            title: title of station
        """
        client = SMHI()
        assert client.get_stations_from_title(parameter_title)

    @pytest.mark.parametrize(
        "parameter, station, distance", [(8, 180960, None), (8, 180960, 50)]
    )
    @patch("smhi.metobs.Stations.__new__")
    @patch("smhi.metobs.Periods.__new__")
    @patch("smhi.metobs.Data.__new__")
    @patch("smhi.smhi.SMHI._interpolate")
    def test_unit_get_data(
        self,
        mock_interpolate,
        mock_data_data,
        mock_period_data,
        mock_station_data,
        parameter,
        station,
        distance,
    ):
        mock_interpolate.return_value = "test"
        client = SMHI()
        data = client.get_data(parameter, station, distance)
        assert data == "test"

    @pytest.mark.parametrize(
        "parameter, city, distance", [(8, "Bengtsfors", None), (8, "Bengtsfors", 50)]
    )
    @patch("smhi.metobs.Stations.__new__")
    @patch("smhi.metobs.Periods.__new__")
    @patch("smhi.metobs.Data.__new__")
    @patch("smhi.smhi.SMHI._find_stations_by_city")
    @patch("smhi.smhi.SMHI._interpolate")
    def test_unit_get_data_by_city(
        self,
        mock_interpolate,
        mock_find_stations_by_city,
        mock_data_data,
        mock_period_data,
        mock_station_data,
        parameter,
        city,
        distance,
    ):
        mock_interpolate.return_value = "test"
        client = SMHI()
        data = client.get_data_by_city(parameter, city, distance)
        assert data == "test"

    distanceresponse = MagicMock()
    distanceresponse.km = 0

    @pytest.mark.parametrize(
        "latitude, longitude,dist",
        [
            (
                59,
                17,
                0,
            ),
            (
                59.4,
                17,
                30,
            ),
        ],
    )
    @patch("geopy.distance.distance", return_value=distanceresponse)
    def test_find_stations_from_gps(self, mock_distance, latitude, longitude, dist):
        """Unit test for SMHI find_stations_from_gps method.

        Args:
        """
        station1 = MagicMock()
        station1.id = 1
        station1.name = "Akalla"
        station1.latitude = 59.5
        station1.longitude = 17.8
        stations = MagicMock()
        stations.station = [station1]

        client = SMHI()
        nearby_town = client._find_stations_from_gps(
            stations, latitude, longitude, dist
        )
        assert nearby_town[0][0] == 1

    @pytest.mark.parametrize(
        "parameter, city, distance", [(8, "Bengtsfors", None), (8, "Bengtsfors", 50)]
    )
    @patch("smhi.metobs.Stations.__new__")
    @patch("smhi.metobs.Periods.__new__")
    @patch("smhi.metobs.Data.__new__")
    @patch("geopy.geocoders.Nominatim.__new__")
    @patch("smhi.smhi.SMHI._find_stations_from_gps")
    def test_find_stations_by_city(
        self,
        mock_find_from_gps,
        mock_nominatim,
        mock_data_data,
        mock_period_data,
        mock_station_data,
        parameter,
        city,
        distance,
    ):
        """Unit test for SMHI _find_stations_by_city method.

        Args:
        """
        client = SMHI()
        data = client._find_stations_by_city(parameter, city, distance)
        mock_nominatim.assert_called_once()

    @pytest.mark.parametrize("distance", [(0), (50)])
    @patch("smhi.metobs.Stations.__new__")
    @patch("smhi.metobs.Periods.__new__")
    @patch("smhi.metobs.Data.__new__")
    @patch("smhi.smhi.SMHI._iterate_over_time")
    @patch("smhi.smhi.SMHI._find_missing_data")
    @patch("smhi.smhi.SMHI._find_stations_from_gps")
    def test_interpolate(
        self,
        mock_find_from_gps,
        mock_find_missing_data,
        mock_iterate_over_time,
        mock_data_data,
        mock_period_data,
        mock_station_data,
        distance,
    ):
        """Unit test for SMHI _interpolate method.

        Args:
        """
        client = SMHI()
        data = client._interpolate(
            distance, mock_station_data, mock_period_data, mock_data_data
        )
        if distance <= 0:
            assert data == mock_data_data
        else:
            mock_find_from_gps.assert_called_once()

    def test_iterate_over_time(
        self,
    ):
        """Unit test for SMHI _iterate_over_time method.

        Args:
        """
        df = pd.DataFrame(
            {
                "date": [
                    "2024-04-21 10:00",
                    "2024-04-21 11:00",
                    "2024-04-21 12:00",
                    "2024-04-22 12:00",
                ],
                "Temperatur": [1, 1, 1, 12],
            }
        )
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        nearby_df = pd.DataFrame(
            {"date": ["2024-04-22 10:00", "2024-04-22 11:00"], "Temperatur": [8, 9]}
        )
        nearby_df["date"] = pd.to_datetime(nearby_df["date"])
        nearby_df = nearby_df.set_index("date")

        missing_df = df[
            df.index.to_series().diff() > df.index.to_series().diff().median()
        ]

        client = SMHI()

        data = client._iterate_over_time(df, nearby_df, missing_df)
        assert data.tail(2).iloc[0]["Temperatur"] == nearby_df.iloc[0]["Temperatur"]

    def test_find_missing_data(
        self,
    ):
        """Unit test for SMHI _find_missing_data method.

        Args:
        """
        df = pd.DataFrame(
            {
                "date": [
                    "2024-04-21 10:00",
                    "2024-04-21 11:00",
                    "2024-04-21 12:00",
                    "2024-04-22 12:00",
                ],
                "Temperatur": [1, 1, 1, 12],
            }
        )
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        client = SMHI()

        missingdata = client._find_missing_data(df)
        assert missingdata.iloc[0]["Temperatur"] == df.iloc[-1]["Temperatur"]
