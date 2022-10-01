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
)


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
        if data_type is None:
            client = MetObs()
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
    def test_unit_metobs_fetch_parameters(
        self,
        mock_metobsparameterv1,
        version,
    ):
        """
        Unit test for MetObs fetch_parameters method.

        Args:
            mock_metobsparameterv1: mock of MetObsParameterV1
            version: version of api
        """
        client = MetObs()

        if version is None:
            client.fetch_parameters()
        if version != "1.0" and version != 1:
            with pytest.raises(NotImplementedError):
                client.fetch_parameters(version)
            return None
        else:
            client.fetch_parameters(version)

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
    def test_unit_metobs_fetch_stations(
        self,
        mock_metobsstationv1,
        parameter,
        parameter_title,
        expected_station,
    ):
        """
        Unit test for MetObs fetch_stations method.

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
                client.fetch_stations()

            with pytest.raises(NotImplementedError):
                client.fetch_stations(parameter, parameter_title)
        elif parameter:
            client.fetch_stations(parameter)
            assert client.station == expected_station
        else:
            client.fetch_stations(parameter_title=parameter_title)
            assert client.station == expected_station

        if parameter or parameter_title:
            mock_metobsstationv1.assert_called_once()

    @pytest.mark.parametrize(
        "station, stationset, expected_period",
        [(None, None, None), ("S1", None, "P1"), (None, "S2", "P2")],
    )
    @patch("smhi.metobs.MetObsPeriodV1", return_value=1)
    def test_unit_metobs_fetch_periods(
        self,
        mock_metobsperiodv1,
        station,
        stationset,
        expected_period,
    ):
        """
        Unit test for MetObs fetch_stations method.

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
                client.fetch_periods()

            with pytest.raises(NotImplementedError):
                client.fetch_periods(station, stationset)
        elif station:
            client.fetch_periods(station)
            assert client.period == expected_period
        else:
            client.fetch_periods(stationset=stationset)
            assert client.period == expected_period

        if station or stationset:
            mock_metobsperiodv1.assert_called_once()


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
    def test_unit_metobslevelv1_fetch_and_parse_request(
        self, mock_json_loads, mock_requests_get
    ):
        """
        Unit test for MetObsLevelV1 _fetch_and_parse_request method.

        Args:
            mock_json_loads: mock json loads method
            mock_requests_get: mock requests get method
        """
        level = MetObsLevelV1()
        url = "URL"

        content = level._fetch_and_parse_request(url)
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
            ([], 1, None),
        ],
    )
    @patch("smhi.metobs.tuple")
    @patch("smhi.metobs.sorted")
    @patch("smhi.metobs.MetObsLevelV1._fetch_and_parse_request")
    @patch("smhi.metobs.MetObsLevelV1._get_url")
    def test_unit_metobsparameterv1_init(
        self,
        mock_get_url,
        mock_fetch_and_parse_request,
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
            mock_fetch_and_parse_request: mock _fetch_and_parse_request get method
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
        else:
            if ("1.0" if version == 1 else version) != "1.0":
                with pytest.raises(NotImplementedError):
                    MetObsParameterV1(data, version, data_type)

                return None

        parameter = MetObsParameterV1(data, version, data_type)
        assert parameter.resource == mock_sorted.return_value
        assert parameter.data == mock_tuple.return_value
        mock_get_url.assert_called_once()
        mock_fetch_and_parse_request.assert_called_once()
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
            (
                [],
                None,
                None,
                "json",
            ),
            ([], None, None, "json"),
        ],
    )
    @patch("smhi.metobs.tuple")
    @patch("smhi.metobs.sorted")
    @patch("smhi.metobs.MetObsLevelV1._fetch_and_parse_request")
    @patch("smhi.metobs.MetObsLevelV1._get_url")
    def test_unit_metobsstationv1_init(
        self,
        mock_get_url,
        mock_fetch_and_parse_request,
        mock_sorted,
        mock_tuple,
        data,
        parameter,
        parameter_title,
        data_type,
    ):
        """
        Unit test for MetObs init method.

        Args:
            mock_get_url: mock of _get_url method
            mock_fetch_and_parse_request: mock of _fetch_and_parse_request method
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

        assert (
            station.valuetype == mock_fetch_and_parse_request.return_value["valueType"]
        )
        assert (
            station.stationset
            == mock_fetch_and_parse_request.return_value["stationSet"]
        )
        assert station.station == mock_sorted.return_value
        assert station.data == mock_tuple.return_value
        mock_get_url.assert_called_once()
        mock_fetch_and_parse_request.assert_called_once()
