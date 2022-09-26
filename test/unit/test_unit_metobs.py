"""
SMHI MetObs unit tests.
"""
import pytest
import unittest
from unittest.mock import patch
from smhi.metobs import MetObs


class TestUnitMetObs:
    """
    Unit tests for MetObs class.
    """

    @pytest.mark.parametrize(
        "data_type, expected_type",
        [(None, "application/json"), ("json", "application/json")],
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

    def test_unit_smhi_init_raise(self):
        """
        Unit test for MetObs init method raising error.
        """
        with pytest.raises(NotImplementedError, match=""):
            MetObs("yaml")
