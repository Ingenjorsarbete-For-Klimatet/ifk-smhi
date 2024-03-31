"""SMHI Metfcts v1 unit tests."""

from unittest.mock import patch

import arrow
import pytest
from smhi.metfcts import Metfcts

BASE_URL = (
    "https://opendata-download-metfcst.smhi.se/" + "api/category/pmp3g/version/2/"
)


class TestUnitMetfcts:
    """Unit tests for Metfcts class."""

    @pytest.mark.parametrize(
        "test_time, expected_answer",
        [
            ("2024-03-31T14:00:00Z", False),
            ("2024-03-31T15:00:00Z", True),
            ("2024-04-10T00:00:00Z", True),
            ("2024-04-11T01:00:00Z", False),
        ],
    )
    @patch("smhi.metfcts.Metfcts._get_parameters")
    @patch("smhi.metfcts.arrow.now", return_value=arrow.get("2024-03-31T15:14:10Z"))
    def test_check_valid_time(
        self, mock_arrow_now, mock_get_parameters, test_time, expected_answer
    ):
        """Unit test _ceck_valid_time."""
        client = Metfcts()
        assert client._check_valid_time(test_time) is expected_answer
