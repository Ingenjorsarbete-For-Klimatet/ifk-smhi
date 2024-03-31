"""SMHI Strang unit tests."""

import datetime
from functools import partial
from unittest.mock import patch

import arrow
import pandas as pd
import pytest
from dateutil.tz import tzutc
from smhi.constants import (
    STRANG_MULTIPOINT_URL,
    STRANG_PARAMETERS,
    STRANG_POINT_URL,
)
from smhi.models.strang_model import StrangParameter
from smhi.strang import Strang

INPUT_DAILY_2020_01_01_2020_01_02 = [
    {"date_time": datetime.datetime(2020, 1, 1, 0, 0, tzinfo=tzutc()), "value": 608.0},
    {"date_time": datetime.datetime(2020, 1, 2, 0, 0, tzinfo=tzutc()), "value": 12.1},
]
INPUT_MULTIPOINT_2020_01_01_MONTHLY_10 = [
    {"lat": 71.139084, "lon": -9.659227, "value": 4.3},
    {"lat": 71.1481, "lon": -9.589094, "value": 4.3},
    {"lat": 71.157104, "lon": -9.5189, "value": 4.3},
    {"lat": 71.16608, "lon": -9.448643, "value": 4.4},
    {"lat": 71.175026, "lon": -9.378324, "value": 4.4},
    {"lat": 71.18395, "lon": -9.307943, "value": 4.4},
    {"lat": 71.19285, "lon": -9.237501, "value": 4.4},
    {"lat": 71.20173, "lon": -9.166997, "value": 4.4},
    {"lat": 71.21058, "lon": -9.096432, "value": 4.3},
    {"lat": 71.219406, "lon": -9.025805, "value": 4.3},
]
RESULT_DAILY_2020_01_01_2020_01_02 = pd.read_csv(
    "tests/fixtures/strang/STRANG_RESULT_DAILY_2020_01_01_2020_01_02.csv",
    parse_dates=[0],
    index_col=0,
)
RESULT_MULTIPOINT_2020_01_01_MONTHLY_10 = pd.read_csv(
    "tests/fixtures/strang/STRANG_RESULT_MULTIPOINT_2020_01_01_MONTHLY_10.csv",
    index_col=0,
)


CATEGORY = "strang1g"
VERSION = 1


class TestUnitStrang:
    """Unit tests for Strang class."""

    def test_unit_strang_init(self):
        """Unit test for Strang init method."""
        client = Strang()

        assert client._category == CATEGORY
        assert client._version == VERSION
        assert client._available_parameters == STRANG_PARAMETERS

        raw_url_dict = {"category": CATEGORY, "version": VERSION}
        for k1, k2 in zip(
            sorted(raw_url_dict.keys()), sorted(client._point_raw_url.keywords.keys())
        ):
            assert k1 == k2
            assert raw_url_dict[k1] == client._point_raw_url.keywords[k2]

        raw_url_dict = {"category": CATEGORY, "version": VERSION}
        for k1, k2 in zip(
            sorted(raw_url_dict.keys()),
            sorted(client._multipoint_raw_url.keywords.keys()),
        ):
            assert k1 == k2
            assert raw_url_dict[k1] == client._multipoint_raw_url.keywords[k2]

    @patch("smhi.strang.logger.info")
    def test_unit_strang_parameters(self, mock_logging):
        """Unit test for Strang parameters get property.

        Args:
            mock_logging: mock of logging info
        """
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
            (0, 0, STRANG_PARAMETERS[116], None, None, None),
            (0, 0, STRANG_PARAMETERS[116], "2020-01-01", "2020-01-01", "hourly"),
            (0, None, STRANG_PARAMETERS[116], "2020-01-01", "2020-01-01", "hourly"),
            (None, 0, STRANG_PARAMETERS[116], "2020-01-01", "2020-01-01", "hourly"),
            (None, None, STRANG_PARAMETERS[116], "2020-01-01", "2020-01-01", "hourly"),
        ],
    )
    @patch(
        "smhi.strang.Strang._get_and_load_data",
        return_value=[
            pd.DataFrame(
                [2.0],
                columns=["value"],
                index=pd.Series([arrow.get("2020-01-01").datetime], name="date_time"),
            ),
            {"head": "head"},
            200,
        ],
    )
    @patch("smhi.strang.Strang._build_time_point_url", return_value="URL")
    def test_unit_strang_get_point(
        self,
        mock_build_time_point_url,
        mock_get_and_load_data,
        lat,
        lon,
        parameter,
        time_from,
        time_to,
        time_interval,
    ):
        """Unit test for Strang get_point method.

        Args:
            mock_build_time_point_url: mock _build_time_point_url method
            mock_get_and_load_data: mock _get_and_load_data method
            lat: latitude
            lon: longitude
            parameter: parameter
            time_from: from time
            time_to: to time
            time_interval: time interval
        """
        client = Strang()

        if parameter.key is None:
            with pytest.raises(NotImplementedError):
                client.get_point(
                    lat,
                    lon,
                    parameter.key,
                    time_from,
                    time_to,
                    time_interval,
                )

            return None

        if lon is None or lat is None:
            mock_get_and_load_data.return_value[0] = False
            with pytest.raises(TypeError):
                client.get_point(
                    lat,
                    lon,
                    parameter.key,
                    time_from,
                    time_to,
                    time_interval,
                )

            return None

        point_model = client.get_point(
            lat,
            lon,
            parameter.key,
            time_from,
            time_to,
            time_interval,
        )

        assert point_model.parameter_key == parameter.key
        assert point_model.parameter_meaning == parameter.meaning
        assert point_model.longitude == lon
        assert point_model.latitude == lat
        assert point_model.time_interval == time_interval
        assert point_model.url == mock_build_time_point_url.return_value
        assert point_model.status == 200
        assert point_model.headers == {"head": "head"}

        mock_build_time_point_url.assert_called_once()
        mock_get_and_load_data.assert_called_once()

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
    @patch(
        "smhi.strang.Strang._get_and_load_data",
        return_value=[
            pd.DataFrame({"lat": [71.0], "lon": [-9.0], "value": [2.0]}),
            {"head": "head"},
            200,
        ],
    )
    @patch("smhi.strang.Strang._build_time_multipoint_url", return_value="URL")
    def test_unit_strang_get_multipoint(
        self,
        mock_build_time_multipoint_url,
        mock_get_and_load_data,
        parameter,
        valid_time,
        time_interval,
    ):
        """Unit test for Strang get_multipoint method.

        Args:
            mock_build_time_multipoint_url: mock _build_time_multipoint_url method
            mock_get_and_load_data: mock _get_and_load_data method
            parameter: parameter
            valid_time: valid time to query
            time_interval: time interval
        """
        client = Strang()

        if parameter.key is None:
            with pytest.raises(NotImplementedError):
                client.get_multipoint(
                    parameter.key,
                    valid_time,
                    time_interval,
                )

            return None

        if valid_time is None:
            with pytest.raises(TypeError):
                client.get_multipoint(
                    parameter.key,
                    valid_time,
                    time_interval,
                )

            return None

        multipoint_model = client.get_multipoint(
            parameter.key,
            valid_time,
            time_interval,
        )

        assert multipoint_model.parameter_key == parameter.key
        assert multipoint_model.parameter_meaning == parameter.meaning
        assert multipoint_model.valid_time == arrow.get(valid_time).isoformat()
        assert multipoint_model.time_interval == time_interval
        assert multipoint_model.url == mock_build_time_multipoint_url.return_value
        assert multipoint_model.status == 200
        assert multipoint_model.headers == {"head": "head"}

        mock_build_time_multipoint_url.assert_called_once()
        mock_get_and_load_data.assert_called_once()

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
        """Unit test for Strang _build_base_point_url method.

        Args:
            lat: latitude
            lon: longitude
            parameter: parmeter
        """
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
        """Unit test for Strang _build_base_point_url method.

        Args:
            parameter: parmeter
            valid_time: valid time
        """
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
        """Unit test for Strang _build_time_point_url method.

        Args:
            mock_parse_datetime: mock of _parse_datetime method
            time_from: from date
            time_to: to date
            time_interval: interval of date
            expected_url: expected URL
        """
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
        """Unit test for Strang _build_time_multipoint_url method.

        Args:
            time_interval: interval of date
            expected_url: expected URL
        """
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
        "status_expected, data",
        [
            (200, [{"date_time": "2020-01-01T00:00:00Z"}]),
            (200, [{"lat": 0, "lon": 0, "value": 0}]),
            (200, [{"date_time": "2020-01-01T00:00:00Z"}]),
        ],
    )
    @patch("smhi.strang.Strang._parse_multipoint_data")
    @patch("smhi.strang.Strang._parse_point_data")
    @patch("smhi.strang.logging.info")
    @patch(
        "smhi.utils.requests.get",
        return_value=type(
            "MyClass",
            (object,),
            {"status_code": 200, "headers": "header", "content": "content"},
        )(),
    )
    @patch(
        "smhi.strang.json.loads", return_value=[{"date_time": "2020-01-01T00:00:00Z"}]
    )
    def test_unit_strang_get_and_load_data(
        self,
        mock_json_loads,
        mock_requests_get,
        mock_logging,
        mock_parse_point_data,
        mock_parse_multipoint_data,
        status_expected,
        data,
    ):
        """Unit test for Strang Point get_and_load_strang_data method."""
        client = Strang()
        client.url = "URL"
        mock_json_loads.return_value = data
        mock_requests_get.return_value.status_code = status_expected

        data, headers, status = client._get_and_load_data(client.url, "parameter")
        mock_requests_get.assert_called_once_with(client.url, timeout=200)

        if status == 200:
            mock_json_loads.assert_called_once_with(
                mock_requests_get.return_value.content
            )
            assert status == status_expected
            assert headers == "header"

            if "date_time" in data[0]:
                mock_parse_point_data.assert_called_once()
            else:
                mock_parse_point_data.mock_parse_multipoint_data()

            mock_logging.assert_not_called()

        else:
            assert status is status_expected
            assert headers == "header"
            pd.testing.assert_frame_equal(data, pd.DataFrame())
            mock_logging.assert_called_once()

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
        """Unit test for Strang _parse_datetime method.

        Args:
            parameter: selected parameter
            date: input data to parse
            expected: expected result
        """
        client = Strang()

        if date_time == "Q" or date_time == "1900":
            with pytest.raises(ValueError):
                client._parse_datetime(date_time, parameter)
        else:
            assert client._parse_datetime(date_time, parameter) == expected

    @pytest.mark.parametrize(
        "parameter, valid_time, time_interval, input, output",
        [
            (
                118,
                None,
                None,
                INPUT_DAILY_2020_01_01_2020_01_02,
                RESULT_DAILY_2020_01_01_2020_01_02,
            ),
        ],
    )
    def test_unit_strang_parse_point_data(
        self, parameter, valid_time, time_interval, input, output
    ):
        """Unit test for Strang _parse_point_data.

        Args:
            parameter: data parameter
            valid_time: valid_time for multipoint
            time_interval: time_interval for multipoint
            input: input data
            output: output data
        """
        client = Strang()
        data = client._parse_point_data(input)

        pd.testing.assert_frame_equal(data, output)

    @pytest.mark.parametrize(
        "parameter, valid_time, time_interval, input, output",
        [
            (
                116,
                "2020-01-01",
                "monthly",
                INPUT_MULTIPOINT_2020_01_01_MONTHLY_10,
                RESULT_MULTIPOINT_2020_01_01_MONTHLY_10,
            ),
        ],
    )
    def test_unit_strang_parse_multipoint_data(
        self, parameter, valid_time, time_interval, input, output
    ):
        """Unit test for Strang _parse_multipoint_data.

        Args:
            parameter: data parameter
            valid_time: valid_time for multipoint
            time_interval: time_interval for multipoint
            input: input data
            output: output data
        """
        client = Strang()
        data = client._parse_multipoint_data(input)

        pd.testing.assert_frame_equal(data, output)
