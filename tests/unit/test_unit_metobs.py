"""SMHI Metobs v1 unit tests."""

from typing import Optional
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from pydantic import BaseModel
from smhi.constants import METOBS_AVAILABLE_PERIODS
from smhi.metobs import (
    BaseMetobs,
    Data,
    Parameters,
    Periods,
    Stations,
    Versions,
)
from smhi.models.metobs_model import (
    MetobsCategoryModel,
    MetobsParameterModel,
    MetobsPeriodModel,
    MetobsStationModel,
    MetobsVersionItem,
    MetobsVersionModel,
)
from utils import MockResponse, get_data, get_response


class MockModelInner(BaseModel):
    href: Optional[str] = None
    type: Optional[str] = None


class MockModel(BaseModel):
    key: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    link: list[MockModelInner]


class MockVersions:
    def __init__(self, data):
        self.data = data


class MockParameters:
    def __init__(self, resource, data):
        self.resource = resource
        self.data = data


class MockStations:
    def __init__(self, data, station=None, stationset=None):
        self.stations = station
        self.stationset = stationset
        self.data = data


class MockPeriods:
    def __init__(self, period, data):
        self.periods = period
        self.data = data


@pytest.fixture
def setup_versions():
    """Read in Versions response."""
    mocked_response = get_response("tests/fixtures/metobs/versions.txt")
    mocked_model = MetobsCategoryModel.model_validate_json(mocked_response.content)

    return mocked_response, mocked_model


@pytest.fixture
def setup_parameters(setup_versions):
    """Read in Parameters response."""
    _, mocked_model_versions = setup_versions

    mocked_response = get_response("tests/fixtures/metobs/parameters.txt")
    mocked_model = MetobsVersionModel.model_validate_json(mocked_response.content)
    mocked_data = tuple(
        MetobsVersionItem.model_validate_json(x)
        for x in get_data("tests/fixtures/metobs/parameters_data.json")
    )

    return (
        mocked_response,
        mocked_model,
        mocked_model_versions,
        mocked_data,
    )


@pytest.fixture
def setup_stations(setup_parameters):
    """Read in Stations response."""
    _, mocked_model_parameters, _, _ = setup_parameters

    mocked_response = get_response("tests/fixtures/metobs/stations.txt")
    mocked_model = MetobsParameterModel.model_validate_json(mocked_response.content)
    mocked_data = tuple(
        [tuple(x) for x in get_data("tests/fixtures/metobs/stations_data.json")]
    )

    return (
        mocked_response,
        mocked_model,
        mocked_model_parameters,
        mocked_data,
    )


@pytest.fixture
def setup_periods(setup_stations):
    """Read in Periods response."""
    _, mocked_model_stations, _, _ = setup_stations

    mocked_response = get_response("tests/fixtures/metobs/periods.txt")
    mocked_model = MetobsStationModel.model_validate_json(mocked_response.content)
    mocked_data = tuple(get_data("tests/fixtures/metobs/periods_data.json"))

    return (
        mocked_response,
        mocked_model,
        mocked_model_stations,
        mocked_data,
    )


@pytest.fixture
def setup_periods_set(setup_stations):
    """Read in Periods for station_set."""
    _, mocked_model_stations, _, _ = setup_stations

    mocked_response = get_response("tests/fixtures/metobs/periods_set.txt")
    mocked_model = MetobsStationModel.model_validate_json(mocked_response.content)
    mocked_data = tuple(get_data("tests/fixtures/metobs/periods_data_set.json"))

    return (
        mocked_response,
        mocked_model,
        mocked_model_stations,
        mocked_data,
    )


@pytest.fixture
def setup_data(setup_periods):
    """Read in Data response."""
    _, mocked_model_periods, _, _ = setup_periods

    mocked_response = get_response("tests/fixtures/metobs/data.txt", encode=True)
    mocked_model = MetobsPeriodModel.model_validate_json(mocked_response.content)
    mocked_csv_data = MockResponse(
        200, None, get_data("tests/fixtures/metobs/data.csv", "data")
    )

    mocked_station = pd.read_csv("tests/fixtures/metobs/data_station.csv", index_col=0)
    mocked_parameter = pd.read_csv(
        "tests/fixtures/metobs/data_parameter.csv", index_col=0
    )
    mocked_period = pd.read_csv("tests/fixtures/metobs/data_period.csv", index_col=0)
    mocked_data = pd.read_csv("tests/fixtures/metobs/data_data.csv", index_col=0)
    mocked_data.index = pd.to_datetime(mocked_data.index)

    return (
        mocked_response,
        mocked_model,
        mocked_model_periods,
        mocked_csv_data,
        mocked_station,
        mocked_parameter,
        mocked_period,
        mocked_data,
    )


class TestUnitBaseMetobs:
    """Unit tests for BaseMetobs class."""

    mock_model_1 = MockModel(
        **{
            "key": "p1",
            "summary": "sum",
            "link": [MockModelInner(**{"href": "URL", "type": "application/json"})],
        }
    )

    mock_model_2 = MockModel(
        **{
            "title": "p2",
            "summary": "sum",
            "link": [MockModelInner(**{"href": "URL", "type": "application/json"})],
        }
    )

    mock_model_3 = MockModel(**{"key": "p1", "link": []})

    def test_unit_basemetobs_init(self):
        """Unit test for BaseMetobs init method."""
        base = BaseMetobs()

        assert base.headers is None
        assert base.key is None
        assert base.updated is None
        assert base.title is None
        assert base.summary is None
        assert base.link is None

    @patch("smhi.utils.requests.get", return_value=MockResponse(200, None, None))
    def test_unit_basemetobs_get_and_parse_request(self, mock_requests_get):
        """Unit test for BaseMetobs _get_and_parse_request method."""
        base = BaseMetobs()
        url = "URL"

        mock_model = MagicMock()
        model = base._get_and_parse_request(url, mock_model)
        mock_requests_get.called_once()

        assert base.headers == mock_requests_get.return_value.headers
        assert base.key == model.key
        assert base.updated == model.updated
        assert base.title == model.title
        assert base.summary == model.summary
        assert base.link == model.link
        assert model == mock_model.model_validate_json.return_value

    @pytest.mark.parametrize(
        "data, key, parameters, data_type, expected_url, expected_summary",
        [
            ([mock_model_1], "key", "p1", "application/json", "URL", "sum"),
            ([mock_model_2], "title", "p2", "application/json", "URL", "sum"),
            ([mock_model_3], "key", "p1", None, IndexError, None),
            ([MockModel(**{"link": []})], "key", "p1", None, IndexError, None),
            ([MockModel(**{"link": []})], "key", None, None, IndexError, None),
            ([MockModel(**{"link": []})], None, None, None, TypeError, None),
        ],
    )
    def test_unit_basemetobs_get_url(
        self, data, key, parameters, data_type, expected_url, expected_summary
    ):
        """Unit test for BaseMetobs _get_url method."""
        base = BaseMetobs()

        if not isinstance(expected_url, str):
            with pytest.raises(expected_url):
                base._get_url(data, key, parameters, data_type)
            return None

        url, summary = base._get_url(data, key, parameters, data_type)

        assert base.data_type == data_type
        assert url == expected_url
        assert summary == expected_summary


class TestUnitVersions:
    """Unit tests for Versionss class."""

    @pytest.mark.parametrize("data_type", [("json"), ("yaml"), ("xml"), (None)])
    @patch("smhi.utils.requests.get")
    def test_unit_versions_init(self, mock_requests_get, data_type, setup_versions):
        """Unit test for Parameters init method."""
        mock_response, expected_answer = setup_versions
        mock_requests_get.return_value = mock_response

        if data_type != "json":
            with pytest.raises(TypeError):
                Versions(data_type)

            return None

        versions = Versions(data_type)

        assert versions.headers == mock_response.headers
        assert versions.key == expected_answer.key
        assert versions.updated == expected_answer.updated
        assert versions.title == expected_answer.title
        assert versions.summary == expected_answer.summary
        assert versions.link == expected_answer.link

        assert versions.data == expected_answer.version


class TestUnitParameters:
    """Unit tests for Parameters class."""

    @pytest.mark.parametrize(
        "supply_versions, version, data_type",
        [
            (True, "1.0", "json"),
            (True, 1, "json"),
            (True, 1, "yaml"),
            (True, None, "json"),
            (True, None, None),
            (False, None, None),
        ],
    )
    @patch("smhi.metobs.Versions")
    @patch("smhi.utils.requests.get")
    def test_unit_parameters_init(
        self,
        mock_requests_get,
        mock_versions_object,
        supply_versions,
        version,
        data_type,
        setup_parameters,
    ):
        """Unit test for Parameters init method."""
        mock_response, expected_answer, mock_versions, expected_data = setup_parameters
        mock_requests_get.return_value = mock_response

        if supply_versions is False:
            mock_versions_object.return_value = mock_versions
            Parameters()

            return None

        if data_type != "json":
            with pytest.raises(TypeError):
                Parameters(mock_versions, version, data_type)

            return None

        if ("1.0" if version == 1 else version) != "1.0":
            with pytest.raises(NotImplementedError):
                Parameters(mock_versions, version, data_type)

            return None

        parameters = Parameters(mock_versions, version, data_type)

        assert parameters.versions_object == mock_versions
        assert parameters.selected_version == "1.0" if version == 1 else version
        assert parameters.resource == expected_answer.resource
        assert parameters.data == expected_data


class TestUnitStations:
    """Unit tests for Stations class."""

    @pytest.mark.parametrize(
        "parameter, parameter_title, data_type",
        [
            (None, None, "yaml"),
            (None, None, "json"),
            ("1", None, "json"),
            (None, "Lufttemperatur", "json"),
            ("1", "Lufttemperatur", "json"),
            ("1", "Lufttemperatur", None),
        ],
    )
    @patch("smhi.utils.requests.get")
    def test_unit_stations_init(
        self,
        mock_requests_get,
        parameter,
        parameter_title,
        data_type,
        setup_stations,
    ):
        """Unit test for Stations init method."""
        mock_response, expected_answer, mock_parameters, expected_data = setup_stations
        mock_requests_get.return_value = mock_response

        if data_type != "json":
            with pytest.raises(TypeError):
                Stations(mock_parameters, parameter, parameter_title, data_type)
            return None

        if parameter is None and parameter_title is None:
            with pytest.raises(NotImplementedError):
                Stations(mock_parameters, parameter, parameter_title, data_type)
            return None

        if parameter and parameter_title:
            with pytest.raises(NotImplementedError):
                Stations(mock_parameters, parameter, parameter_title, data_type)
            return None

        stations = Stations(mock_parameters, parameter, parameter_title, data_type)

        if parameter:
            assert stations.selected_parameter == parameter

        if parameter_title:
            assert stations.selected_parameter == parameter_title

        assert stations.value_type == expected_answer.value_type
        assert stations.station_set == expected_answer.station_set
        assert stations.station == expected_answer.station
        assert stations.data == expected_data


class TestUnitPeriods:
    """Unit tests for Periods class."""

    @pytest.mark.parametrize(
        "station, station_name, stationset, data_type",
        [
            (None, None, None, "yaml"),
            (None, None, None, "json"),
            (1, None, None, "json"),
            (None, "Akalla", None, "json"),
            (None, None, "all", "json"),
            (1, "Akalla", None, "json"),
            (1, None, "all", "json"),
            (None, "Akalla", "all", "json"),
            (1, "Akalla", "all", "json"),
        ],
    )
    @patch("smhi.utils.requests.get")
    def test_unit_periods_init(
        self,
        mock_requests_get,
        station,
        station_name,
        stationset,
        data_type,
        setup_periods,
        setup_periods_set,
    ):
        """Unit test for Periods init method."""
        if stationset is None:
            mock_response, expected_answer, mock_stations, expected_data = setup_periods
            mock_requests_get.return_value = mock_response
        else:
            (
                mock_response,
                expected_answer,
                mock_stations,
                expected_data,
            ) = setup_periods_set
            mock_requests_get.return_value = mock_response

        if data_type != "json":
            with pytest.raises(TypeError):
                Periods(mock_stations, station, station_name, stationset, data_type)
            return None

        if [station, station_name, stationset].count(None) == 3:
            with pytest.raises(NotImplementedError):
                Periods(mock_stations, station, station_name, stationset, data_type)
            return None

        if [bool(x) for x in [station, station_name, stationset]].count(True) > 1:
            with pytest.raises(NotImplementedError):
                Periods(mock_stations, station, station_name, stationset, data_type)
            return None

        periods = Periods(mock_stations, station, station_name, stationset, data_type)

        if station:
            assert periods.selected_station == station

        if station_name:
            assert periods.selected_station == station_name

        if stationset:
            assert periods.selected_station == stationset

        assert periods.owner == expected_answer.owner
        assert periods.owner_category == expected_answer.owner_category
        assert periods.measuring_stations == expected_answer.measuring_stations
        assert periods.active == expected_answer.active
        assert periods.time_from == expected_answer.from_
        assert periods.time_to == expected_answer.to
        assert periods.position == expected_answer.position
        assert periods.period == expected_answer.period
        assert periods.data == expected_data


class TestUnitData:
    """Unit tests for Data class."""

    @pytest.mark.parametrize(
        "period, data_type",
        [
            ("latest", "yaml"),
            (None, "json"),
            ("latest", "json"),
            ("corrected-archive", "json"),
        ],
    )
    @patch("smhi.utils.requests.get")
    def test_unit_data_init(
        self,
        mock_requests_get,
        period,
        data_type,
        setup_data,
    ):
        """Unit test for Data init method."""
        (
            mock_response,
            expected_answer,
            mock_periods,
            expected_table_data,
            expected_station,
            expected_parameter,
            expected_period,
            expected_data,
        ) = setup_data
        mock_requests_get.side_effect = [mock_response, expected_table_data]

        if data_type != "json":
            with pytest.raises(TypeError):
                Data(mock_periods, period, data_type)
            return None

        if period not in METOBS_AVAILABLE_PERIODS and period is not None:
            with pytest.raises(NotImplementedError):
                Data(mock_periods, period, data_type)
            return None

        data = Data(mock_periods, period, data_type)

        assert data.time_from == expected_answer.from_
        assert data.time_to == expected_answer.to
        pd.testing.assert_frame_equal(data.station, expected_station)
        pd.testing.assert_frame_equal(data.parameter, expected_parameter)
        pd.testing.assert_frame_equal(data.period, expected_period)
        pd.testing.assert_frame_equal(data.df, expected_data)
