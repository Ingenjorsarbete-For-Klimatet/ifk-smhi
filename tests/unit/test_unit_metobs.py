"""SMHI Metobs v1 unit tests."""
import json
import pytest
import pandas as pd
from codecs import encode, decode
from unittest.mock import patch, MagicMock
from smhi.metobs import (
    Metobs,
    BaseLevel,
    Versions,
    Parameters,
    Stations,
    Periods,
    Data,
)
from smhi.constants import METOBS_AVAILABLE_PERIODS


with open("tests/fixtures/unit_metobs_data.txt") as f:
    METOBS_DATA = decode(
        encode(f.readline(), "latin-1", "backslashreplace"), "unicode-escape"
    )
    METOBS_NODATA = decode(
        encode(f.readline(), "latin-1", "backslashreplace"), "unicode-escape"
    )

METOBS_DATA_RESULT = pd.read_csv(
    "tests/fixtures/metobs_data.csv", parse_dates=[0], index_col=0
)
METOBS_NODATA_RESULT: None = None


with open("tests/fixtures/metobs_unit_1.json") as f:
    METOBS_UNIT_1 = json.load(f)

with open("tests/fixtures/metobs_unit_2.json") as f:
    METOBS_UNIT_2 = json.load(f)


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
        mock_requests_get.assert_called_once()
        mock_json_loads.assert_called_once()

    @pytest.mark.parametrize("version", [("1.0"), ("latest"), (1), (None)])
    @patch("smhi.metobs.Parameters")
    def test_unit_metobs_get_parameters(
        self,
        mock_parameters,
        version,
    ):
        """Unit test for Metobs get_parameters method.

        Args:
            mock_parameters: mock of Parameters
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
        assert client.parameters == mock_parameters.return_value
        mock_parameters.assert_called_once()

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
        mock_stations,
        parameters,
        parameters_title,
        client_parameters,
        expected_station,
    ):
        """Unit test for Metobs get_stations method.

        Args:
            mock_stations: mock of Stations
            parameters: parameters of api
            parameters_title: parameters title of api
            client_parameters: client parameters
            expected_station: expected stations
        """
        client = Metobs()
        client.parameters = client_parameters
        mock_stations.return_value = expected_station

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
            mock_stations.assert_called_once()

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
        mock_period,
        stations,
        stationset,
        client_stations,
        expected_period,
    ):
        """Unit test for Metobs get_stations method.

        Args:
            mock_period: mock of Periods
            stations: stations of api
            stationset: stations set of api
            client_stations: client stations
            expected_period: expected periods
        """
        client = Metobs()
        client.stations = client_stations
        mock_period.return_value = expected_period

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
            mock_period.assert_called_once()

    @pytest.mark.parametrize("client_periods", [(MagicMock()), (None)])
    @patch("smhi.metobs.Data")
    def test_unit_metobs_get_data(self, mock_data, client_periods):
        """Unit test for Metobs get_data method.

        Args:
            mock_data: mock of metobs data class
            client_periods: client periods
        """
        client = Metobs()
        client.periods = client_periods

        if client_periods is None:
            assert client.get_data() == (None, None)
            return

        data, data_header = client.get_data()

        assert data == mock_data.return_value.data
        assert data_header == mock_data.return_value.data_header
        mock_data.assert_called_once()

    @patch("smhi.metobs.Metobs.get_parameters")
    @patch("smhi.metobs.Metobs.get_stations")
    @patch("smhi.metobs.Metobs.get_periods")
    @patch("smhi.metobs.Metobs.get_data", return_value=("test1", "header1"))
    def test_unit_metobs_get_data_from_selection(
        self,
        mock_get_data,
        mock_get_periods,
        mock_get_stations,
        mock_get_parameters,
    ):
        """Unit test for Metobs get_data method.

        Args:
            mock_get_parameters
            mock_get_stations
            mock_get_periods
            mock_get_data
        """
        client = Metobs()
        data, data_header = client.get_data_from_selection(1, 1, "1")

        mock_get_parameters.assert_called_once()
        mock_get_stations.assert_called_once()
        mock_get_periods.assert_called_once()
        mock_get_data.assert_called_once()

        assert data == mock_get_data.return_value[0]
        assert data_header == mock_get_data.return_value[1]

    @patch("smhi.metobs.Metobs.get_parameters")
    @patch("smhi.metobs.Metobs.get_stations")
    @patch("smhi.metobs.Metobs.get_periods")
    @patch("smhi.metobs.Metobs.get_data", return_value=("test1", "header1"))
    def test_unit_metobs_get_data_stationset(
        self,
        mock_get_data,
        mock_get_periods,
        mock_get_stations,
        mock_get_parameters,
    ):
        """Unit test for Metobs get_data_stationset method.

        Args:
            mock_get_parameters
            mock_get_stations
            mock_get_periods
            mock_get_data
        """
        client = Metobs()
        data, data_header = client.get_data_stationset(1, 1, "corrected-data")

        mock_get_parameters.assert_called_once()
        mock_get_stations.assert_called_once()
        mock_get_periods.assert_called_once()
        mock_get_data.assert_called_once()

        assert data == mock_get_data.return_value[0]
        assert data_header == mock_get_data.return_value[1]


class TestUnitBaseLevel:
    """Unit tests for BaseLevel class."""

    def test_unit_baselevel_init(self):
        """Unit test for BaseLevel init method."""
        level = BaseLevel()

        assert level.headers is None
        assert level.key is None
        assert level.updated is None
        assert level.title is None
        assert level.summary is None
        assert level.link is None
        assert level.data_type is None
        assert level.raw_data_header is None
        assert level.data_header is None
        assert level.data is None

    def test_baselevel_unit_show(self):
        """Unit test for BaseLevel show property."""
        level = BaseLevel()
        assert level.show is None

    @patch("smhi.metobs.requests.get")
    @patch("smhi.metobs.json.loads")
    def test_unit_baselevel_get_and_parse_request(
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
    def test_unit_baselevel_get_url(
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


class TestUnitVersions:
    """Unit tests for Versionss class."""

    @pytest.mark.parametrize(
        "data_type",
        [("json"), ("yaml"), ("json"), (None)],
    )
    @patch("smhi.metobs.tuple")
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    def test_unit_versions_init(
        self,
        mock_get_and_parse_request,
        mock_tuple,
        data_type,
    ):
        """Unit test for Parameters init method.

        Args:
            mock_get_and_parse_request: mock _get_and_parse_request get method
            mock_tuple: mock of tuple call
            data_type: format of api data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                Versions(data_type)

            return None

        versions = Versions(data_type)
        assert versions.data == mock_tuple.return_value
        mock_get_and_parse_request.assert_called_once()
        mock_tuple.assert_called_once()


class TestUnitParameter:
    """Unit tests for Parameters class."""

    @pytest.mark.parametrize(
        "versions, version, data_type",
        [
            (MagicMock(), "1.0", "json"),
            (MagicMock(), 1, "json"),
            (MagicMock(), 1, "yaml"),
            (MagicMock(), None, "json"),
            (MagicMock(), None, None),
            (None, "1.0", "json"),
        ],
    )
    @patch("smhi.metobs.tuple")
    @patch("smhi.metobs.sorted")
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    @patch("smhi.metobs.Versions")
    def test_unit_parameters_init(
        self,
        mock_versions,
        mock_get_url,
        mock_get_and_parse_request,
        mock_sorted,
        mock_tuple,
        versions,
        version,
        data_type,
    ):
        """Unit test for Parameters init method.

        Args:
            mock_versions: mock of Versions class
            mock_get_url: mock _get_url method
            mock_get_and_parse_request: mock _get_and_parse_request get method
            mock_sorted: mock of sorted call
            mock_tuple: mock of tuple call
            versions: versions object
            version: version of API
            data_type: format of api data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                Parameters(versions, version, data_type)

            return None

        if ("1.0" if version == 1 else version) != "1.0":
            with pytest.raises(NotImplementedError):
                Parameters(versions, version, data_type)

            return None

        parameters = Parameters(versions, version, data_type)
        assert parameters.resource == mock_sorted.return_value
        assert parameters.data == mock_tuple.return_value
        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()
        mock_sorted.assert_called_once()
        mock_tuple.assert_called_once()

        if versions is None:
            mock_versions.assert_called_once()


class TestUnitStation:
    """Unit tests for Stations class."""

    @pytest.mark.parametrize(
        "parameters, parameter, parameter_title, data_type",
        [
            (MagicMock(), None, None, "yaml"),
            (MagicMock(), None, None, "json"),
            (MagicMock(), "key", None, "json"),
            (MagicMock(), None, "title", "json"),
            (MagicMock(), "key", "title", "json"),
            (MagicMock(), "key", "title", None),
        ],
    )
    @patch("smhi.metobs.tuple")
    @patch("smhi.metobs.sorted")
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    def test_unit_stations_init(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        mock_sorted,
        mock_tuple,
        parameters,
        parameter,
        parameter_title,
        data_type,
    ):
        """Unit test for Stations init method.

        Args:
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            mock_sorted: mock sorted call
            mock_tuple: mock tuple call
            parameters: parameter object
            parameter: parameter
            parameter_title: parameter title
            data_type: type of data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                Stations(parameters, parameter, parameter_title, data_type)
            return None

        if parameter is None and parameter_title is None:
            with pytest.raises(NotImplementedError):
                Stations(parameters, parameter, parameter_title, data_type)
            return None

        if parameter and parameter_title:
            with pytest.raises(NotImplementedError):
                Stations(parameters, parameter, parameter_title, data_type)
            return None

        stations = Stations(parameters, parameter, parameter_title, data_type)

        if parameter:
            assert stations.selected_parameter == parameter

        if parameter_title:
            assert stations.selected_parameter == parameter_title

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


class TestUnitPeriod:
    """Unit tests for Periods class."""

    @pytest.mark.parametrize(
        "stations, station, station_name, stationset, data_type",
        [
            (MagicMock(), None, None, None, "yaml"),
            (MagicMock(), None, None, None, "json"),
            (MagicMock(), "p1", None, None, "json"),
            (MagicMock(), None, "p2", None, "json"),
            (MagicMock(), None, None, "p3", "json"),
            (MagicMock(), "p1", "p2", None, "json"),
            (MagicMock(), "p1", None, "p3", "json"),
            (MagicMock(), None, "p2", "p3", "json"),
            (MagicMock(), "p1", "p2", "p3", "json"),
        ],
    )
    @patch("smhi.metobs.sorted")
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    def test_unit_periods_init(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        mock_sorted,
        stations,
        station,
        station_name,
        stationset,
        data_type,
    ):
        """Unit test for Periods init method.

        Args:
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            mock_sorted: mock sorted call
            stations: stations object
            station: station
            station_name: stations name
            stationset: stations set
            data_type: type of data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                Periods(stations, station, station_name, stationset, data_type)
            return None

        if [station, station_name, stationset].count(None) == 3:
            with pytest.raises(NotImplementedError):
                Periods(stations, station, station_name, stationset, data_type)
            return None

        if [bool(x) for x in [station, station_name, stationset]].count(True) > 1:
            with pytest.raises(NotImplementedError):
                Periods(stations, station, station_name, stationset, data_type)
            return None

        periods = Periods(stations, station, station_name, stationset, data_type)

        if station:
            assert periods.selected_station == station

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
        assert periods.data == ()

        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()
        mock_sorted.assert_called_once()


class TestUnitData:
    """Unit tests for Data class."""

    @pytest.mark.parametrize(
        "periods, period, data_type",
        [
            (MagicMock(), None, "yaml"),
            (MagicMock(), None, "json"),
            (MagicMock(), "latest-hour", "json"),
            (MagicMock(), "latest", "json"),
            (MagicMock(), "latest-months", "json"),
            (MagicMock(), "corrected-archive", "json"),
        ],
    )
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    @patch("smhi.metobs.Data._get_data")
    def test_unit_data_init(
        self,
        mock_get_data,
        mock_get_url,
        mock_get_and_parse_request,
        periods,
        period,
        data_type,
    ):
        """Unit test for Data init method.

        Args:
            mock_get_data: mock of _get_data method
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            period: period object
            period: period
            data_type: type of data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                Data(periods, period, data_type)
            return None

        if period not in METOBS_AVAILABLE_PERIODS:
            with pytest.raises(NotImplementedError):
                Data(periods, period, data_type)
            return None

        data = Data(periods, period, data_type)

        assert data.selected_period == period
        assert data.time_from == mock_get_and_parse_request.return_value["from"]
        assert data.time_to == mock_get_and_parse_request.return_value["to"]
        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()

    @pytest.mark.parametrize(
        "periods, period, data_type, data_type_init, raise_error",
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
    @patch("smhi.metobs.Data._parse_header")
    @patch("smhi.metobs.Data._parse_data")
    def test_unit_data_get_data(
        self,
        mock_parse_data,
        mock_parse_header,
        mock_get_url,
        mock_get_and_parse_request,
        mock_request_get,
        periods,
        period,
        data_type,
        data_type_init,
        raise_error,
    ):
        """Unit test for Data get method.

        Args:
            mock_parse_data: mock of _parse_data
            mock_parse_header: mock of _parse_header
            mock_get_url: mock of _get_url
            mock_get_and_parse_request: mock of _get_and_parse_request
            mock_request_get: mock of requests get method
            periods: periods object
            period: period
            data_type_init: data type init
            data_type: data type
            raise_error: raise error or not
        """
        data_object = Data(MagicMock(), period, data_type_init)
        data_object.raw_data = periods
        data_object._get_data(data_type)

        if raise_error is True:
            return

        mock_request_get.assert_called_once()
        mock_parse_data.assert_called_once_with(data_object.raw_data)
        mock_parse_header.assert_called_once_with(data_object.raw_data_header)

    @pytest.mark.parametrize(
        "content, header, data",
        [
            ("Test, Datum, Test2", "Test, ", "Datum, Test"),
        ],
    )
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    @patch("smhi.metobs.Data._get_data")
    def test_unit_data_separate_header_data(
        self,
        _get_data,
        mock_get_url,
        mock_get_and_parse_request,
        content,
        header,
        data,
    ):
        """Unit test for Data separate header data.

        Args:
            _get_data: mock of _get_data
            mock_get_url: mock of _get_url
            mock_get_and_parse_request: mock of _get_and_parse_request
            content: content string
            header: header
            data: data
        """
        data_object = Data(MagicMock(), "corrected-archive", "json")

        raw_data_header, raw_data = data_object._separate_header_data(content)
        assert raw_data_header == header
        assert raw_data == data

    @pytest.mark.parametrize(
        "data, result_header",
        [(METOBS_DATA, METOBS_UNIT_1)],
    )
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    @patch("smhi.metobs.Data._get_data")
    def test_unit_data_parse_header(
        self,
        _get_data,
        mock_get_url,
        mock_get_and_parse_request,
        data,
        result_header,
    ):
        """Unit test for Data get method.

        Args:
            _get_data: mock of _get_data
            mock_get_url: mock of _get_url
            mock_get_and_parse_request: mock of _get_and_parse_request
            data: data
            result: expected result
            result_header: expected parsed header
        """
        data_object = Data(MagicMock(), "corrected-archive", "json")

        raw_data_header, _ = data_object._separate_header_data(data)
        data_object._parse_header(raw_data_header)
        assert data_object.data_header == result_header

    @pytest.mark.parametrize(
        "data, result",
        [
            (METOBS_DATA, METOBS_DATA_RESULT),
            (METOBS_NODATA, METOBS_NODATA_RESULT),
        ],
    )
    @patch("smhi.metobs.BaseLevel._get_and_parse_request")
    @patch("smhi.metobs.BaseLevel._get_url")
    @patch("smhi.metobs.Data._get_data")
    def test_unit_data_parse_data(
        self,
        _get_data,
        mock_get_url,
        mock_get_and_parse_request,
        data,
        result,
    ):
        """Unit test for Data get method.

        Args:
            _get_data: mock of _get_data
            mock_get_url: mock of _get_url
            mock_get_and_parse_request: mock of _get_and_parse_request
            data: data
            result: expected result
        """
        data_object = Data(MagicMock(), "corrected-archive", "json")

        if result is None:
            with pytest.raises(TypeError):
                data_object._separate_header_data(data)
                data_object._parse_data(data_object.raw_data)
            return

        _, raw_data = data_object._separate_header_data(data)
        data_object._parse_data(raw_data)
        pd.testing.assert_frame_equal(data_object.data, result)
