"""Test utils functions."""

import pytest
from smhi.utils import format_datetime


class Utils:
    @pytest.mark.parametrize(
        "test_time, expected_answer",
        [
            ("2024-03-31T07", "20240331T070000Z"),
            ("2024-03-31T06:00", "20240331T060000Z"),
            ("2024-03-30T07:00:00", "20240330T070000Z"),
            ("2024-03-30T060000", "20240330T060000Z"),
            ("2024-03-30T060000Z", "20240330T060000Z"),
        ],
    )
    def test_format_datetime(self, test_time, expected_answer):
        """Unit test _format_datetime."""
        assert format_datetime(test_time) == expected_answer
