"""SMHI Strang unit tests."""

from functools import partial
from unittest.mock import patch

import arrow
import pandas as pd
import pytest
from smhi.constants import (
    STRANG_MULTIPOINT_URL,
    STRANG_PARAMETERS,
    STRANG_POINT_URL,
)
from smhi.models.strang_model import StrangParameter
from smhi.strang import Strang
from utils import get_response


@pytest.fixture
def setup_point():
    """Read in Point response."""
    mocked_response = get_response("tests/fixtures/strang/point.txt")
    mocked_data = pd.read_csv(
        "tests/fixtures/strang/point_data.csv", index_col="date_time"
    )
    mocked_data.index = pd.to_datetime(mocked_data.index)

    return mocked_response, mocked_data


@pytest.fixture
def setup_multipoint():
    """Read in MultiPoint response."""
    mocked_response = get_response("tests/fixtures/strang/multipoint.txt")
    mocked_data = pd.read_csv("tests/fixtures/strang/multipoint_data.csv", index_col=0)

    return mocked_response, mocked_data


CATEGORY = "strang1g"
VERSION = 1


def helper_test_partial_string(raw_url):
    raw_url_dict = {"category": CATEGORY, "version": VERSION}
    for k1, k2 in zip(sorted(raw_url_dict.keys()), sorted(raw_url.keywords.keys())):
        assert k1 == k2
        assert raw_url_dict[k1] == raw_url.keywords[k2]


class TestUnitStrang:
    """Unit tests for Strang class."""

    def test_unit_strang_init(self):
        """Unit test for Strang init method."""
        client = Strang()

        assert client._category == CATEGORY
        assert client._version == VERSION
        assert client._available_parameters == STRANG_PARAMETERS

        helper_test_partial_string(client._point_raw_url)
        helper_test_partial_string(client._multipoint_raw_url)

    @patch("smhi.strang.logger.info")
    def test_unit_strang_parameters(self, mock_logging):
        """Unit test for Strang parameters get property."""
        client = Strang()
        assert client.parameters == list(STRANG_PARAMETERS.keys())
        assert mock_logging.call_count == len(STRANG_PARAMETERS)

    @pytest.mark.parametrize(
        "lat, lon, parameter, time_from, time_to, time_interval",
        [
            (
                0,
                0,
                StrangParameter(key=None, meaning=None, time_from=None, time_to=None),
                "2020-01-01",
                "2020-01-01",
                "hourly",
            ),
            (0, None, STRANG_PARAMETERS[116], "2020-01-01", "2020-01-01", "hourly"),
            (None, 0, STRANG_PARAMETERS[116], "2020-01-01", "2020-01-01", "hourly"),
            (None, None, STRANG_PARAMETERS[116], "2020-01-01", "2020-01-01", "hourly"),
            (0, 0, STRANG_PARAMETERS[116], None, None, None),
            (0, 0, STRANG_PARAMETERS[116], "2020-01-01", "2020-01-01", "hourly"),
        ],
    )
    @patch("smhi.utils.requests.get")
    def test_unit_strang_get_point(
        self,
        mock_requests_get,
        lat,
        lon,
        parameter,
        time_from,
        time_to,
        time_interval,
        setup_point,
    ):
        """Unit test for Strang get_point method."""
        (mock_response, expected_answer) = setup_point
        mock_requests_get.return_value = mock_response

        client = Strang()

        if parameter.key is None:
            with pytest.raises(NotImplementedError):
                client.get_point(
                    lat, lon, parameter.key, time_from, time_to, time_interval
                )

            return None

        if lon is None or lat is None:
            with pytest.raises(ValueError):
                client.get_point(
                    lat, lon, parameter.key, time_from, time_to, time_interval
                )

            return None

        point = client.get_point(
            lat, lon, parameter.key, time_from, time_to, time_interval
        )

        assert point.parameter_key == parameter.key
        assert point.parameter_meaning == parameter.meaning
        assert point.longitude == lon
        assert point.latitude == lat
        assert point.time_interval == time_interval
        assert point.url is not None
        assert point.status == mock_response.status_code
        assert point.headers == mock_response.headers
        pd.testing.assert_frame_equal(point.df, expected_answer)

    @pytest.mark.parametrize(
        "parameter, valid_time, time_interval",
        [
            (
                StrangParameter(key=None, meaning=None, time_from=None, time_to=None),
                "2020-01-01",
                "hourly",
            ),
            (STRANG_PARAMETERS[116], "2020-01-01", "hourly"),
            (STRANG_PARAMETERS[116], "2020-01-01", "hourly"),
            (STRANG_PARAMETERS[116], None, None),
            (STRANG_PARAMETERS[116], None, None),
        ],
    )
    @patch("smhi.utils.requests.get")
    def test_unit_strang_get_multipoint(
        self, mock_requests_get, parameter, valid_time, time_interval, setup_multipoint
    ):
        """Unit test for Strang get_multipoint method."""
        (mock_response, expected_answer) = setup_multipoint
        mock_requests_get.return_value = mock_response

        client = Strang()

        if parameter.key is None:
            with pytest.raises(NotImplementedError):
                client.get_multipoint(parameter.key, valid_time, time_interval)

            return None

        if valid_time is None:
            with pytest.raises(TypeError):
                client.get_multipoint(parameter.key, valid_time, time_interval)

            return None

        multipoint = client.get_multipoint(parameter.key, valid_time, time_interval)

        assert multipoint.parameter_key == parameter.key
        assert multipoint.parameter_meaning == parameter.meaning
        assert multipoint.valid_time == arrow.get(valid_time).datetime
        assert multipoint.time_interval == time_interval
        assert multipoint.url is not None
        assert multipoint.status == mock_response.status_code
        assert multipoint.headers == mock_response.headers
        pd.testing.assert_frame_equal(multipoint.df, expected_answer)

    @pytest.mark.parametrize(
        "lat, lon, parameter",
        [
            (
                None,
                None,
                StrangParameter(key=None, meaning=None, time_from=None, time_to=None),
            ),
            ("16", "50", STRANG_PARAMETERS[116]),
        ],
    )
    def test_unit_strang_build_base_point_url(self, lat, lon, parameter):
        """Unit test for Strang _build_base_point_url method."""
        client = Strang()

        url = partial(STRANG_POINT_URL.format, category=CATEGORY, version=VERSION)
        url = url(lon=lon, lat=lat, parameter=parameter.key)

        base_url = client._build_base_point_url(
            client._point_raw_url, parameter, lon, lat
        )

        assert base_url == url

    @pytest.mark.parametrize(
        "parameter, valid_time",
        [
            (
                StrangParameter(key=None, meaning=None, time_from=None, time_to=None),
                None,
            ),
            (STRANG_PARAMETERS[116], "2020-01-01"),
        ],
    )
    def test_unit_strang_build_base_multipoint_url(self, parameter, valid_time):
        """Unit test for Strang _build_base_point_url method."""
        client = Strang()

        url = partial(STRANG_MULTIPOINT_URL.format, category=CATEGORY, version=VERSION)
        url = url(parameter=parameter.key, validtime=valid_time)

        base_url = client._build_base_multipoint_url(
            client._multipoint_raw_url, parameter, valid_time
        )

        assert base_url == url

    @pytest.mark.parametrize(
        "time_from, time_to, time_interval, expected_url",
        [
            (None, None, None, "URL"),
            ("2020-01-01", None, None, "URL?from=2020-01-01"),
            (None, "2020-01-01", None, "URL?to=2020-01-01"),
            ("2020-01-01", "2020-01-02", None, "URL?from=2020-01-01&to=2020-01-02"),
            ("2020-01-01", "2020-01-02", "bad", None),
            (
                "2020-01-01",
                "2020-01-02",
                "hourly",
                "URL?from=2020-01-01&to=2020-01-02&interval=hourly",
            ),
            (None, None, "notimplemented", None),
        ],
    )
    @patch("smhi.strang.Strang._parse_datetime")
    def test_unit_strang_build_time_point_url(
        self, mock_parse_datetime, time_from, time_to, time_interval, expected_url
    ):
        """Unit test for Strang _build_time_point_url method."""
        client = Strang()
        mock_parse_datetime.side_effect = [time_from, time_to]

        client.url = "URL"

        if time_interval == "bad":
            with pytest.raises(ValueError):
                client._build_time_point_url(
                    client.url, time_from, time_to, time_interval
                )
        elif time_interval == "notimplemented":
            with pytest.raises(NotImplementedError):
                client._build_time_point_url(
                    client.url, time_from, time_to, time_interval
                )
        else:
            assert expected_url == client._build_time_point_url(
                client.url, time_from, time_to, time_interval
            )

    @pytest.mark.parametrize(
        "time_interval, expected_url",
        [(None, "URL"), ("hourly", "URL?interval=hourly"), ("notimplemented", None)],
    )
    def test_unit_strang_build_time_multipoint_url(self, time_interval, expected_url):
        """Unit test for Strang _build_time_multipoint_url method."""
        client = Strang()

        client.url = "URL"

        if time_interval == "notimplemented":
            with pytest.raises(ValueError):
                client._build_time_multipoint_url(client.url, time_interval)
        else:
            assert expected_url == client._build_time_multipoint_url(
                client.url, time_interval
            )

    @pytest.mark.parametrize(
        "parameter, date_time, expected",
        [
            (STRANG_PARAMETERS[0], None, None),
            (STRANG_PARAMETERS[0], "Q", None),
            (STRANG_PARAMETERS[116], "1900", None),
            (STRANG_PARAMETERS[116], "2000", arrow.get("2000").isoformat()),
        ],
    )
    def test_unit_strang_parse_datetime(self, parameter, date_time, expected):
        """Unit test for Strang _parse_datetime method."""
        client = Strang()

        if date_time == "Q" or date_time == "1900":
            with pytest.raises(ValueError):
                client._parse_datetime(date_time, parameter)
        else:
            assert client._parse_datetime(date_time, parameter) == expected
