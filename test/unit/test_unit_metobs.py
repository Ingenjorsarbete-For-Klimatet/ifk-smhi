"""
SMHI MetObs v1 unit tests.
"""
import pytest
from unittest.mock import patch, MagicMock
from smhi.metobs import (
    MetObs,
    MetObsLevelV1,
    MetObsParameterV1,
    MetObsStationV1,
    MetObsPeriodV1,
    MetObsDataV1,
)
from smhi.constants import METOBS_AVAILABLE_PERIODS


class TestUnitMetObs:
    """
    Unit tests for MetObs class.
    """

    @pytest.mark.parametrize(
        "data_type, expected_type",
        [(None, "application/json"), ("json", "application/json"), ("yaml", None)],
    )
    @patch("smhi.metobs.requests.get")
    @patch("smhi.metobs.json.loads")
    def test_unit_metobs_init(
        self, mock_requests_get, mock_json_loads, data_type, expected_type
    ):
        """
        Unit test for MetObs init method.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
            data_type: format of api data
            expected_type: expected result
        """
        if data_type != "json":
            with pytest.raises(NotImplementedError):
                MetObs("yaml")
            return None
        else:
            client = MetObs(data_type)

        assert client.data_type == expected_type
        assert client.version is None
        assert client.parameter is None
        assert client.station is None
        assert client.period is None
        assert client.data is None
        assert client.table_raw is None
        assert client.table is None
        mock_requests_get.assert_called_once()
        mock_json_loads.assert_called_once()

    @pytest.mark.parametrize("version", [("1.0"), ("latest"), (1)])
    @patch("smhi.metobs.MetObsParameterV1")
    def test_unit_metobs_get_parameters(
        self,
        mock_metobsparameterv1,
        version,
    ):
        """
        Unit test for MetObs get_parameters method.

        Args:
            mock_metobsparameterv1: mock of MetObsParameterV1
            version: version of api
        """
        client = MetObs()

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
        assert client.parameter == mock_metobsparameterv1.return_value
        mock_metobsparameterv1.assert_called_once()

    @pytest.mark.parametrize(
        "parameter, parameter_title, expected_station",
        [(None, None, None), ("P1", None, "S1"), (None, "P2", "S2")],
    )
    @patch("smhi.metobs.MetObsStationV1", return_value=1)
    def test_unit_metobs_get_stations(
        self,
        mock_metobsstationv1,
        parameter,
        parameter_title,
        expected_station,
    ):
        """
        Unit test for MetObs get_stations method.

        Args:
            mock_metobsstationv1: mock of MetObsStationV1
            parameter: parameter of api
            parameter_title: parameter title of api
            expected_station: expected station
        """
        client = MetObs()
        client.parameter = MagicMock()
        mock_metobsstationv1.return_value = expected_station

        if parameter is None and parameter_title is None:
            with pytest.raises(NotImplementedError):
                client.get_stations()

            with pytest.raises(NotImplementedError):
                client.get_stations(parameter, parameter_title)
        elif parameter:
            client.get_stations(parameter)
            assert client.station == expected_station
        else:
            client.get_stations(parameter_title=parameter_title)
            assert client.station == expected_station

        if parameter or parameter_title:
            mock_metobsstationv1.assert_called_once()

    @pytest.mark.parametrize(
        "station, stationset, expected_period",
        [(None, None, None), ("S1", None, "P1"), (None, "S2", "P2")],
    )
    @patch("smhi.metobs.MetObsPeriodV1", return_value=1)
    def test_unit_metobs_get_periods(
        self,
        mock_metobsperiodv1,
        station,
        stationset,
        expected_period,
    ):
        """
        Unit test for MetObs get_stations method.

        Args:
            mock_metobsperiodv1: mock of MetObsPeriodV1
            station: station of api
            stationset: station set of api
            expected_period: expected period
        """
        client = MetObs()
        client.station = MagicMock()
        mock_metobsperiodv1.return_value = expected_period

        if station is None and stationset is None:
            with pytest.raises(NotImplementedError):
                client.get_periods()

            with pytest.raises(NotImplementedError):
                client.get_periods(station, stationset)
        elif station:
            client.get_periods(station)
            assert client.period == expected_period
        else:
            client.get_periods(stationset=stationset)
            assert client.period == expected_period

        if station or stationset:
            mock_metobsperiodv1.assert_called_once()

    @patch("smhi.metobs.io.StringIO")
    @patch("smhi.metobs.pd.read_csv")
    @patch("smhi.metobs.MetObsDataV1")
    def test_unit_metobs_get_data(
        self, mock_metobsdatav1, mock_pd_read_csv, mock_stringio
    ):
        """
        Unit test for MetObs get_data method.

        Args:
            mock_metobsdatav1: mock of metobs data class
            mock_pd_read_csv: mock of pandas read_csv
            mock_stringio: mock of io StringIO
        """
        client = MetObs()
        client.period = MagicMock()
        client.get_data()

        assert client.data == mock_metobsdatav1.return_value
        assert client.table_raw == mock_metobsdatav1.return_value.get()
        assert client.table == mock_pd_read_csv.return_value

        mock_metobsdatav1.assert_called_once()
        mock_pd_read_csv.assert_called_once()
        mock_stringio.assert_called_once()

    @patch("smhi.metobs.MetObs.get_parameters")
    @patch("smhi.metobs.MetObs.get_stations")
    @patch("smhi.metobs.MetObs.get_periods")
    @patch("smhi.metobs.MetObs.get_data")
    def test_unit_metobs_get_data_from_selection(
        self,
        mock_get_parameters,
        mock_get_stations,
        mock_get_periods,
        mock_get_data,
    ):
        """
        Unit test for MetObs get_data method.

        Args:
            mock_get_parameters
            mock_get_stations
            mock_get_periods
            mock_get_data
        """
        client = MetObs()
        client.get_data_from_selection(1, 1, "1")

        mock_get_parameters.assert_called_once()
        mock_get_stations.assert_called_once()
        mock_get_periods.assert_called_once()
        mock_get_data.assert_called_once()

    @patch("smhi.metobs.MetObs.get_parameters")
    @patch("smhi.metobs.MetObs.get_stations")
    @patch("smhi.metobs.MetObs.get_periods")
    @patch("smhi.metobs.MetObs.get_data")
    def test_unit_metobs_get_data_stationset(
        self,
        mock_get_parameters,
        mock_get_stations,
        mock_get_periods,
        mock_get_data,
    ):
        """
        Unit test for MetObs get_data_stationset method.

        Args:
            mock_get_parameters
            mock_get_stations
            mock_get_periods
            mock_get_data
        """
        client = MetObs()
        client.get_data_stationset(1, 1, "1")

        mock_get_parameters.assert_called_once()
        mock_get_stations.assert_called_once()
        mock_get_periods.assert_called_once()
        mock_get_data.assert_called_once()


class TestUnitMetObsLevelV1:
    """
    Unit tests for MetObsLevelV1 class.
    """

    def test_unit_metobslevelv1_init(self):
        """
        Unit test for MetObsLevelV1 init method.
        """
        level = MetObsLevelV1()

        assert level.headers is None
        assert level.key is None
        assert level.updated is None
        assert level.title is None
        assert level.summary is None
        assert level.link is None
        assert level.data_type is None

    @patch("smhi.metobs.requests.get")
    @patch("smhi.metobs.json.loads")
    def test_unit_metobslevelv1_get_and_parse_request(
        self, mock_json_loads, mock_requests_get
    ):
        """
        Unit test for MetObsLevelV1 _get_and_parse_request method.

        Args:
            mock_json_loads: mock json loads method
            mock_requests_get: mock requests get method
        """
        level = MetObsLevelV1()
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
        "data, key, parameter, data_type, expected_result",
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
    def test_unit_metobslevelv1_get_url(
        self, data, key, parameter, data_type, expected_result
    ):
        """
        Unit test for MetObsLevelV1 _get_url method.

        Args:
            data: list of data
            key: key
            parameter: parameter
            data_type: format of api data
            expected_result: expected result
        """
        level = MetObsLevelV1()

        if type(expected_result) != str:
            with pytest.raises(expected_result):
                level._get_url(data, key, parameter, data_type)
            return None

        url = level._get_url(data, key, parameter, data_type)

        assert level.data_type == data_type
        assert url == expected_result


class TestUnitMetObsParameterV1:
    """
    Unit tests for MetObsParameterV1 class.
    """

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
    @patch("smhi.metobs.MetObsLevelV1._get_and_parse_request")
    @patch("smhi.metobs.MetObsLevelV1._get_url")
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
        """
        Unit test for MetObsParameterV1 init method.

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
                MetObsParameterV1(data, version, data_type)

            return None

        if ("1.0" if version == 1 else version) != "1.0":
            with pytest.raises(NotImplementedError):
                MetObsParameterV1(data, version, data_type)

            return None

        parameter = MetObsParameterV1(data, version, data_type)
        assert parameter.resource == mock_sorted.return_value
        assert parameter.data == mock_tuple.return_value
        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()
        mock_sorted.assert_called_once()
        mock_tuple.assert_called_once()


class TestUnitMetObsStationV1:
    """
    Unit tests for MetObsStationV1 class.
    """

    @pytest.mark.parametrize(
        "data, parameter, parameter_title, data_type",
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
    @patch("smhi.metobs.MetObsLevelV1._get_and_parse_request")
    @patch("smhi.metobs.MetObsLevelV1._get_url")
    def test_unit_metobsstationv1_init(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        mock_sorted,
        mock_tuple,
        data,
        parameter,
        parameter_title,
        data_type,
    ):
        """
        Unit test for MetObsStationV1 init method.

        Args:
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            mock_sorted: mock sorted call
            mock_tuple: mock tuple call
            data: data list
            parameter: parameter
            parameter_title: parameter title
            data_type: type of data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                MetObsStationV1(data, parameter, parameter_title, data_type)
            return None

        if parameter is None and parameter_title is None:
            with pytest.raises(NotImplementedError):
                MetObsStationV1(data, parameter, parameter_title, data_type)
            return None

        if parameter and parameter_title:
            with pytest.raises(NotImplementedError):
                MetObsStationV1(data, parameter, parameter_title, data_type)
            return None

        station = MetObsStationV1(data, parameter, parameter_title, data_type)

        if parameter:
            assert station.selected_parameter == parameter

        if parameter_title:
            assert station.selected_parameter == parameter_title

        assert station.valuetype == mock_get_and_parse_request.return_value["valueType"]
        assert (
            station.stationset == mock_get_and_parse_request.return_value["stationSet"]
        )
        assert station.station == mock_sorted.return_value
        assert station.data == mock_tuple.return_value
        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()
        mock_sorted.assert_called_once()
        mock_tuple.assert_called_once()


class TestUnitMetObsPeriodV1:
    """
    Unit tests for MetObsPeriodV1 class.
    """

    @pytest.mark.parametrize(
        "data, station, station_name, stationset, data_type",
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
    @patch("smhi.metobs.MetObsLevelV1._get_and_parse_request")
    @patch("smhi.metobs.MetObsLevelV1._get_url")
    def test_unit_metobsperiodv1_init(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        mock_sorted,
        data,
        station,
        station_name,
        stationset,
        data_type,
    ):
        """
        Unit test for MetObsPeriodV1 init method.

        Args:
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            mock_sorted: mock sorted call
            data: data list
            station: station
            station_name: station name
            stationset: station set
            data_type: type of data
        """
        if data_type != "json":
            with pytest.raises(TypeError):
                MetObsPeriodV1(data, station, station_name, stationset, data_type)
            return None

        if [station, station_name, stationset].count(None) == 3:
            with pytest.raises(NotImplementedError):
                MetObsPeriodV1(data, station, station_name, stationset, data_type)
            return None

        if [bool(x) for x in [station, station_name, stationset]].count(True) > 1:
            with pytest.raises(NotImplementedError):
                MetObsPeriodV1(data, station, station_name, stationset, data_type)
            return None

        period = MetObsPeriodV1(data, station, station_name, stationset, data_type)

        if station:
            assert period.selected_station == station

        if station_name:
            assert period.selected_station == station_name

        if stationset:
            assert period.selected_station == stationset

        assert period.owner == mock_get_and_parse_request.return_value["owner"]
        assert (
            period.ownercategory
            == mock_get_and_parse_request.return_value["ownerCategory"]
        )
        assert (
            period.measuringstations
            == mock_get_and_parse_request.return_value["measuringStations"]
        )
        assert period.active == mock_get_and_parse_request.return_value["active"]
        assert period.time_from == mock_get_and_parse_request.return_value["from"]
        assert period.time_to == mock_get_and_parse_request.return_value["to"]
        assert period.position == mock_get_and_parse_request.return_value["position"]
        assert period.period == mock_sorted.return_value
        assert period.data == []

        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()
        mock_sorted.assert_called_once()


class TestUnitMetObsDataV1:
    """
    Unit tests for MetObsDataV1 class.
    """

    @pytest.mark.parametrize(
        "data, period, data_type",
        [
            ([], None, "yaml"),
            ([], None, "json"),
            ([], "latest-hour", "json"),
            ([], "latest", "json"),
            ([], "latest-months", "json"),
            ([], "corrected-archive", "json"),
        ],
    )
    @patch("smhi.metobs.MetObsLevelV1._get_and_parse_request")
    @patch("smhi.metobs.MetObsLevelV1._get_url")
    def test_unit_metobsdatav1_init(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        data,
        period,
        data_type,
    ):
        """
        Unit test for MetObsDataV1 init method.

        Args:
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            data: data list
            period: period
            data_type: type of data
        """

        if data_type != "json":
            with pytest.raises(TypeError):
                MetObsDataV1(data, period, data_type)
            return None

        if period not in METOBS_AVAILABLE_PERIODS:
            with pytest.raises(NotImplementedError):
                MetObsDataV1(data, period, data_type)
            return None

        data = MetObsDataV1(data, period, data_type)

        assert data.selected_period == period
        assert data.time_from == mock_get_and_parse_request.return_value["from"]
        assert data.time_to == mock_get_and_parse_request.return_value["to"]
        assert data.data == mock_get_and_parse_request.return_value["data"]
        mock_get_url.assert_called_once()
        mock_get_and_parse_request.assert_called_once()

    @pytest.mark.parametrize(
        "data, period, data_type, data_type_init",
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
            ),
        ],
    )
    @patch("smhi.metobs.requests.get")
    @patch("smhi.metobs.MetObsLevelV1._get_and_parse_request")
    @patch("smhi.metobs.MetObsLevelV1._get_url")
    def test_unit_metobsdatav1_get(
        self,
        mock_get_url,
        mock_get_and_parse_request,
        mock_request_get,
        data,
        period,
        data_type,
        data_type_init,
    ):
        """
        Unit test for MetObsDataV1 get method.

        Args:
            mock_get_url: mock of _get_url method
            mock_get_and_parse_request: mock of _get_and_parse_request method
            mock_request_get: mock of requests get method
            data: data
            period: period
            data_type_init: data type init
            data_type: data type
        """
        data_object = MetObsDataV1(data, period, data_type_init)
        data_object.data = data
        read_data = data_object.get(data_type)
        assert read_data == mock_request_get.return_value.content.decode("utf-8")
        mock_request_get.assert_called_once()
