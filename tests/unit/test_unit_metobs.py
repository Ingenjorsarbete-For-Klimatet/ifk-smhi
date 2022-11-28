"""SMHI Metobs v1 unit tests."""
import pytest
from unittest.mock import patch, MagicMock
from smhi.metobs import (
    Metobs,
    BaseLevel,
    Parameters,
    Stations,
    Periods,
    Data,
)
from smhi.constants import METOBS_AVAILABLE_PERIODS


class TestUnitMetobs:
    """Unit tests for Metobs class."""

    @pytest.mark.parametrize(
        "data_type, expected_type",
        [(None, "application/json"), ("json", "application/json"), ("yaml", None)],
    )
    @patch("smhi.metobs.requests.get")
    @patch("smhi.metobs.json.loads")
    def test_unit_metobs_init(
        self, mock_requests_get, mock_json_loads, data_type, expected_type
    ):
        """Unit test for Metobs init method.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
            data_type: format of api data
            expected_type: expected result
        """
        if data_type != "json":
            with pytest.raises(NotImplementedError):
                Metobs("yaml")
            return None
        else:
            client = Metobs(data_type)

        assert client.data_type == expected_type
        assert client.version is None
        assert client.parameters is None
        assert client.stations is None
        assert client.periods is None
        assert client.data is None
        assert client.table_raw is None
        mock_requests_get.assert_called_once()
        mock_json_loads.assert_called_once()

    @pytest.mark.parametrize("version", [("1.0"), ("latest"), (1)])
    @patch("smhi.metobs.Parameters")
    def test_unit_metobs_get_parameters(
        self,
        mock_metobsparameterv1,
        version,
    ):
        """Unit test for Metobs get_parameters method.

        Args:
            mock_metobsparameterv1: mock of Parameters
            version: version of api
        """
        client = Metobs()

        if version is None:
            client.get_parameters()
        if version != "1.0" and version != 1:
            with pytest.raises(NotImplementedError):
                client.get_parameters(version)
            return None
        else:
            client.get_parameters(version)

        if version == 1:
            version = "1.0"

        assert client.version == version
        assert client.parameters == mock_metobsparameterv1.return_value
        mock_metobsparameterv1.assert_called_once()

    @pytest.mark.parametrize(
        "parameters, parameters_title, client_parameters, expected_station",
        [
            (None, None, MagicMock(), None),
            ("P1", None, MagicMock(), "S1"),
            (None, "P2", MagicMock(), "S2"),
            (None, None, None, None),
        ],
    )
    @patch("smhi.metobs.Stations", return_value=1)
    def test_unit_metobs_get_stations(
        self,
        mock_metobsstationv1,
        parameters,
        parameters_title,
        client_parameters,
        expected_station,
    ):
        """Unit test for Metobs get_stations method.

        Args:
            mock_metobsstationv1: mock of Stations
            parameters: parameters of api
            parameters_title: parameters title of api
            client_parameters: client parameters
            expected_station: expected stations
        """
        client = Metobs()
        client.parameters = client_parameters
        mock_metobsstationv1.return_value = expected_station

        if client_parameters is None:
            assert client.get_stations() is None
            return

        if parameters is None and parameters_title is None:
            with pytest.raises(NotImplementedError):
                client.get_stations()

            with pytest.raises(NotImplementedError):
                client.get_stations(parameters, parameters_title)
        elif parameters:
            client.get_stations(parameters)
            assert client.stations == expected_station
        else:
            client.get_stations(parameter_title=parameters_title)
            assert client.stations == expected_station

        if parameters or parameters_title:
            mock_metobsstationv1.assert_called_once()

    @pytest.mark.parametrize(
        "stations, stationset, client_stations, expected_period",
        [
            (None, None, MagicMock(), None),
            ("S1", None, MagicMock(), "P1"),
            (None, "S2", MagicMock(), "P2"),
            (None, None, None, None),
        ],
    )
    @patch("smhi.metobs.Periods", return_value=1)
    def test_unit_metobs_get_periods(
        self,
        mock_metobsperiodv1,
        stations,
        stationset,
        client_stations,
        expected_period,
    ):
        """Unit test for Metobs get_stations method.

        Args:
            mock_metobsperiodv1: mock of Periods
            stations: stations of api
            stationset: stations set of api
            client_stations: client stations
            expected_period: expected periods
        """
        client = Metobs()
        client.stations = client_stations
        mock_metobsperiodv1.return_value = expected_period

        if client_stations is None:
            assert client.get_periods() is None
            return

        if stations is None and stationset is None:
            with pytest.raises(NotImplementedError):
                client.get_periods()

            with pytest.raises(NotImplementedError):
                client.get_periods(stations, stationset)
        elif stations:
            client.get_periods(stations)
            assert client.periods == expected_period
        else:
            client.get_periods(stationset=stationset)
            assert client.periods == expected_period

        if stations or stationset:
            mock_metobsperiodv1.assert_called_once()

    @pytest.mark.parametrize("client_periods", [(MagicMock()), (None)])
    @patch("smhi.metobs.io.StringIO")
    @patch("smhi.metobs.pd.read_csv")
    @patch("smhi.metobs.Data")
    def test_unit_metobs_get_data(
        self, mock_metobsdatav1, mock_pd_read_csv, mock_stringio, client_periods
    ):
        """Unit test for Metobs get_data method.

        Args:
            mock_metobsdatav1: mock of metobs data class
            mock_pd_read_csv: mock of pandas read_csv
            mock_stringio: mock of io StringIO
            client_periods: client periods
        """
        client = Metobs()
        client.periods = client_periods

        if client_periods is None:
            assert client.get_data() == (None, None)
            return

        client.get_data()

        assert client.data == mock_metobsdatav1.return_value
        assert client.table_raw == mock_metobsdatav1.return_value.get()

        mock_metobsdatav1.assert_called_once()
        mock_pd_read_csv.assert_called_once()
        mock_stringio.assert_called_once()

    @patch("smhi.metobs.Metobs.get_parameters")
    @patch("smhi.metobs.Metobs.get_stations")
    @patch("smhi.metobs.Metobs.get_periods")
    @patch("smhi.metobs.Metobs.get_data", return_value=("test1", "test2"))
    def test_unit_metobs_get_data_from_selection(
        self,
        mock_get_parameters,
        mock_get_stations,
        mock_get_periods,
        mock_get_data,
    ):
        """Unit test for Metobs get_data method.

        Args:
            mock_get_parameters
            mock_get_stations
            mock_get_periods
            mock_get_data
        """
        client = Metobs()
        client.get_data_from_selection(1, 1, "1")

        mock_get_parameters.assert_called_once()
        mock_get_stations.assert_called_once()
        mock_get_periods.assert_called_once()
        mock_get_data.assert_called_once()

    @patch("smhi.metobs.Metobs.get_parameters")
    @patch("smhi.metobs.Metobs.get_stations")
    @patch("smhi.metobs.Metobs.get_periods")
    @patch("smhi.metobs.Metobs.get_data", return_value=("test1", "test2"))
    def test_unit_metobs_get_data_stationset(
        self,
        mock_get_parameters,
        mock_get_stations,
        mock_get_periods,
        mock_get_data,
    ):
        """Unit test for Metobs get_data_stationset method.

        Args:
            mock_get_parameters
            mock_get_stations
            mock_get_periods
            mock_get_data
        """
        client = Metobs()
        client.get_data_stationset(1, 1, "corrected-data")

        mock_get_parameters.assert_called_once()
        mock_get_stations.assert_called_once()
        mock_get_periods.assert_called_once()
        mock_get_data.assert_called_once()


class TestUnitBaseLevel:
    """Unit tests for BaseLevel class."""

    def test_unit_BaseLevel_init(self):
        """Unit test for BaseLevel init method."""
        level = BaseLevel()

        assert level.headers is None
        assert level.key is None
        assert level.updated is None
        assert level.title is None
        assert level.summary is None
        assert level.link is None
        assert level.data_type is None

    @patch("smhi.metobs.requests.get")
    @patch("smhi.metobs.json.loads")
    def test_unit_BaseLevel_get_and_parse_request(
        self, mock_json_loads, mock_requests_get
    ):
        """Unit test for BaseLevel _get_and_parse_request method.

        Args:
            mock_json_loads: mock json loads method
            mock_requests_get: mock requests get method
        """
        level = BaseLevel()
        url = "URL"

        content = level._get_and_parse_request(url)
        mock_json_loads.called_once()
        mock_requests_get.called_once()

        assert level.headers == mock_requests_get.return_value.headers
        assert level.key == mock_json_loads.return_value["key"]
        assert level.updated == mock_json_loads.return_value["updated"]
        assert level.title == mock_json_loads.return_value["title"]
        assert level.summary == mock_json_loads.return_value["summary"]
        assert level.link == mock_json_loads.return_value["link"]
        assert content == mock_json_loads.return_value

    @pytest.mark.parametrize(
        "data, key, parameters, data_type, expected_result",
        [
            (
                [{"key": "p1", "link": [{"href": "URL", "type": "application/json"}]}],
                "key",
                "p1",
                "application/json",
                "URL",
            ),
            (
                [
                    {
                        "title": "p2",
                        "link": [{"href": "URL", "type": "application/json"}],
                    }
                ],
                "title",
                "p2",
                "application/json",
                "URL",
            ),
            ([{"key": "p1", "link": []}], "key", "p1", None, IndexError),
            ([{"link": []}], "key", "p1", None, KeyError),
            ([{"link": []}], "key", None, None, KeyError),
            ([{"link": []}], None, None, None, KeyError),
        ],
    )
    def test_unit_BaseLevel_get_url(
        self, data, key, parameters, data_type, expected_result
    ):
        """Unit test for BaseLevel _get_url method.

        Args:
            data: list of data
            key: key
            parameters: parameters
            data_type: format of api data
            expected_result: expected result
        """
        level = BaseLevel()

        if type(expected_result) != str:
            with pytest.raises(expected_result):
                level._get_url(data, key, parameters, data_type)
            return None

        url = level._get_url(data, key, parameters, data_type)

        assert level.data_type == data_type
        assert url == expected_result


class TestUnitMetObsParameterV1:
    """Unit tests for Parameters class."""

    @pytest.mark.parametrize(
        "data, version, data_type",
        [
            ([], "1.0", "json"),
            ([], 1, "json"),
            ([], 1, "yaml"),
            ([], None, "json"),
            ([], None, None),
        ],
    )
    @patch("smhi.metobs.tuple")
    @patch("smhi.metobs.sorted")
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    def test_unit_metobsparameterv1_init(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        mock_sorted,
        mock_tuple,
        data,
        version,
        data_type,
    ):
        """Unit test for Parameters init method.

        Args:
            mock_get_url: mock _get_url method
            mock_get_and_parse_request: mock _get_and_parse_request get method
            mock_sorted: mock of sorted call
            mock_tuple: mock of tuple call
            data: list of data
            version: version of API
            data_type: format of api data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                Parameters(data, version, data_type)

            return None

        if ("1.0" if version == 1 else version) != "1.0":
            with pytest.raises(NotImplementedError):
                Parameters(data, version, data_type)

            return None

        parameters = Parameters(data, version, data_type)
        assert parameters.resource == mock_sorted.return_value
        assert parameters.data == mock_tuple.return_value
        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()
        mock_sorted.assert_called_once()
        mock_tuple.assert_called_once()


class TestUnitMetObsStationV1:
    """Unit tests for Stations class."""

    @pytest.mark.parametrize(
        "data, parameters, parameters_title, data_type",
        [
            ([], None, None, "yaml"),
            ([], None, None, "json"),
            ([], "key", None, "json"),
            ([], None, "title", "json"),
            ([], "key", "title", "json"),
            ([], "key", "title", None),
        ],
    )
    @patch("smhi.metobs.tuple")
    @patch("smhi.metobs.sorted")
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    def test_unit_metobsstationv1_init(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        mock_sorted,
        mock_tuple,
        data,
        parameters,
        parameters_title,
        data_type,
    ):
        """Unit test for Stations init method.

        Args:
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            mock_sorted: mock sorted call
            mock_tuple: mock tuple call
            data: data list
            parameters: parameters
            parameters_title: parameters title
            data_type: type of data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                Stations(data, parameters, parameters_title, data_type)
            return None

        if parameters is None and parameters_title is None:
            with pytest.raises(NotImplementedError):
                Stations(data, parameters, parameters_title, data_type)
            return None

        if parameters and parameters_title:
            with pytest.raises(NotImplementedError):
                Stations(data, parameters, parameters_title, data_type)
            return None

        stations = Stations(data, parameters, parameters_title, data_type)

        if parameters:
            assert stations.selected_parameter == parameters

        if parameters_title:
            assert stations.selected_parameter == parameters_title

        assert (
            stations.valuetype == mock_get_and_parse_request.return_value["valueType"]
        )
        assert (
            stations.stationset == mock_get_and_parse_request.return_value["stationSet"]
        )
        assert stations.stations == mock_sorted.return_value
        assert stations.data == mock_tuple.return_value
        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()
        mock_sorted.assert_called_once()
        mock_tuple.assert_called_once()


class TestUnitMetObsPeriodV1:
    """Unit tests for Periods class."""

    @pytest.mark.parametrize(
        "data, stations, station_name, stationset, data_type",
        [
            ([], None, None, None, "yaml"),
            ([], None, None, None, "json"),
            ([], "p1", None, None, "json"),
            ([], None, "p2", None, "json"),
            ([], None, None, "p3", "json"),
            ([], "p1", "p2", None, "json"),
            ([], "p1", None, "p3", "json"),
            ([], None, "p2", "p3", "json"),
            ([], "p1", "p2", "p3", "json"),
        ],
    )
    @patch("smhi.metobs.sorted")
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    def test_unit_metobsperiodv1_init(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        mock_sorted,
        data,
        stations,
        station_name,
        stationset,
        data_type,
    ):
        """Unit test for Periods init method.

        Args:
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            mock_sorted: mock sorted call
            data: data list
            stations: stations
            station_name: stations name
            stationset: stations set
            data_type: type of data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                Periods(data, stations, station_name, stationset, data_type)
            return None

        if [stations, station_name, stationset].count(None) == 3:
            with pytest.raises(NotImplementedError):
                Periods(data, stations, station_name, stationset, data_type)
            return None

        if [bool(x) for x in [stations, station_name, stationset]].count(True) > 1:
            with pytest.raises(NotImplementedError):
                Periods(data, stations, station_name, stationset, data_type)
            return None

        periods = Periods(data, stations, station_name, stationset, data_type)

        if stations:
            assert periods.selected_station == stations

        if station_name:
            assert periods.selected_station == station_name

        if stationset:
            assert periods.selected_station == stationset

        assert periods.owner == mock_get_and_parse_request.return_value["owner"]
        assert (
            periods.ownercategory
            == mock_get_and_parse_request.return_value["ownerCategory"]
        )
        assert (
            periods.measuringstations
            == mock_get_and_parse_request.return_value["measuringStations"]
        )
        assert periods.active == mock_get_and_parse_request.return_value["active"]
        assert periods.time_from == mock_get_and_parse_request.return_value["from"]
        assert periods.time_to == mock_get_and_parse_request.return_value["to"]
        assert periods.position == mock_get_and_parse_request.return_value["position"]
        assert periods.periods == mock_sorted.return_value
        assert periods.data == []

        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()
        mock_sorted.assert_called_once()


class TestUnitMetObsDataV1:
    """Unit tests for Data class."""

    @pytest.mark.parametrize(
        "data, periods, data_type",
        [
            ([], None, "yaml"),
            ([], None, "json"),
            ([], "latest-hour", "json"),
            ([], "latest", "json"),
            ([], "latest-months", "json"),
            ([], "corrected-archive", "json"),
        ],
    )
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    def test_unit_metobsdatav1_init(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        data,
        periods,
        data_type,
    ):
        """Unit test for Data init method.

        Args:
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            data: data list
            periods: periods
            data_type: type of data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                Data(data, periods, data_type)
            return None

        if periods not in METOBS_AVAILABLE_PERIODS:
            with pytest.raises(NotImplementedError):
                Data(data, periods, data_type)
            return None

        data = Data(data, periods, data_type)

        assert data.selected_period == periods
        assert data.time_from == mock_get_and_parse_request.return_value["from"]
        assert data.time_to == mock_get_and_parse_request.return_value["to"]
        assert data.data == mock_get_and_parse_request.return_value["data"]
        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()

    @pytest.mark.parametrize(
        "data, periods, data_type, data_type_init, raise_error",
        [
            (
                [
                    {
                        "key": "p1",
                        "link": [
                            {"href": "URL", "type": "application/json"},
                            {"href": "URL", "type": "text/plain"},
                        ],
                    }
                ],
                "corrected-archive",
                "text/plain",
                "json",
                False,
            ),
            (
                [
                    {
                        "key": "p1",
                        "link": [
                            {"href": "URL", "type": "application/json"},
                            {"href": "URL", "type": "text/plain"},
                        ],
                    }
                ],
                "corrected-archive",
                "text/plain",
                "json",
                True,
            ),
        ],
    )
    @patch("smhi.metobs.requests.get")
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    def test_unit_metobsdatav1_get(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        mock_request_get,
        data,
        periods,
        data_type,
        data_type_init,
        raise_error,
    ):
        """Unit test for Data get method.

        Args:
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            mock_request_get: mock of requests get method
            data: data
            periods: periods
            data_type_init: data type init
            data_type: data type
            raise_error: raise error or not
        """
        data_object = Data(data, periods, data_type_init)
        data_object.data = data
        read_data = data_object.get(data_type)

        if raise_error is True:

            return
        assert read_data == mock_request_get.return_value.content.decode("utf-8")
        mock_request_get.assert_called_once()
