"""
SMHI MetObs v1 unit tests.
"""
import pytest
import unittest
from unittest.mock import patch
from smhi.metobs import MetObs, MetObsParameterV1


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
    def test_unit_smhi_init(
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

        assert client.type == expected_type
        assert client.version is None
        assert client.parameter is None
        assert client.station is None
        assert client.period is None
        assert client.data is None
        assert client.table_raw is None
        assert client.table is None
        mock_requests_get.assert_called_once()
        mock_json_loads.assert_called_once()

    @pytest.mark.parametrize(
        "version, expected_type",
        [("1.0", "application/json"), ("latest", "application/json")],
    )
    @patch("smhi.metobs.MetObsParameterV1")
    @patch("smhi.metobs.requests.get")
    @patch("smhi.metobs.json.loads")
    def test_unit_smhi_fetch_parameters(
        self,
        mock_requests_get,
        mock_json_loads,
        mock_metobsparameterv1,
        version,
        expected_type,
    ):
        """
        Unit test for MetObs fetch_parameters method.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
            mock_metobsparameterv1: mock of MetObsParameterV1
            version: version of api
            expected_type: expected result
        """
        client = MetObs()

        if version is None:
            client.fetch_parameters()
        if version != "1.0":
            with pytest.raises(NotImplementedError):
                client.fetch_parameters(version)
            return None
        else:
            client.fetch_parameters(version)

        assert client.version == version
        assert client.parameter == mock_metobsparameterv1.return_value
        mock_metobsparameterv1.assert_called_once()
