"""SMHI Strang unit tests."""
import arrow
import pytest
from functools import partial
from unittest.mock import patch
from smhi.strang import Strang
from smhi.constants import (
    STRANG,
    STRANG_EMPTY,
    STRANG_POINT_URL,
    STRANG_PARAMETERS,
    STRANG_MULTIPOINT_URL,
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

        assert client.latitude is None
        assert client.longitude is None
        assert client.parameter is STRANG_EMPTY
        assert client.status is None
        assert client.header is None
        assert client.data is None
        assert client.available_parameters == STRANG_PARAMETERS

        raw_url_dict = {"category": CATEGORY, "version": VERSION}
        for k1, k2 in zip(
            sorted(raw_url_dict.keys()), sorted(client.point_raw_url.keywords.keys())
        ):
            assert k1 == k2
            assert raw_url_dict[k1] == client.point_raw_url.keywords[k2]

        raw_url_dict = {"category": CATEGORY, "version": VERSION}
        for k1, k2 in zip(
            sorted(raw_url_dict.keys()),
            sorted(client.multipoint_raw_url.keywords.keys()),
        ):
            assert k1 == k2
            assert raw_url_dict[k1] == client.multipoint_raw_url.keywords[k2]

        assert client.point_url is None
        assert client.multipoint_url is None

    @patch("smhi.strang.logging.info")
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
                STRANG(
                    None,
                    None,
                    None,
                    None,
                ),
                "2020-01-01",
                "2020-01-01",
                "hourly",
            ),
            (
                0,
                0,
                STRANG_PARAMETERS[116],
                None,
                None,
                None,
            ),
            (
                0,
                0,
                STRANG_PARAMETERS[116],
                "2020-01-01",
                "2020-01-01",
                "hourly",
            ),
            (
                0,
                None,
                STRANG_PARAMETERS[116],
                "2020-01-01",
                "2020-01-01",
                "hourly",
            ),
            (
                None,
                0,
                STRANG_PARAMETERS[116],
                "2020-01-01",
                "2020-01-01",
                "hourly",
            ),
            (
                None,
                None,
                STRANG_PARAMETERS[116],
                "2020-01-01",
                "2020-01-01",
                "hourly",
            ),
        ],
    )
    @patch(
        "smhi.strang.Strang._get_and_load_data",
        return_value=[None, None, None],
    )
    @patch("smhi.strang.Strang._build_time_point_url")
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

        if parameter.parameter is None:
            with pytest.raises(NotImplementedError):
                client.get_point(
                    lat,
                    lon,
                    parameter.parameter,
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
                    parameter.parameter,
                    time_from,
                    time_to,
                    time_interval,
                )

            return None
        mock_get_and_load_data.return_value = (
            {"date_time": ["2020-01-01 12:00CET"], "value": 2},
            False,
            False,
        )
        client.get_point(
            lat,
            lon,
            parameter.parameter,
            time_from,
            time_to,
            time_interval,
        )

        assert client.longitude == lon
        assert client.latitude == lat
        assert client.parameter == parameter
        assert client.time_interval == time_interval
        assert client.point_url == mock_build_time_point_url.return_value

        mock_build_time_point_url.assert_called_once()
        mock_get_and_load_data.assert_called_once()

    @pytest.mark.parametrize(
        "parameter, valid_time, time_interval",
        [
            (
                STRANG(
                    None,
                    None,
                    None,
                    None,
                ),
                "2020-01-01",
                "hourly",
            ),
            (
                STRANG_PARAMETERS[116],
                "2020-01-01",
                "hourly",
            ),
            (
                STRANG_PARAMETERS[116],
                "2020-01-01",
                "hourly",
            ),
            (
                STRANG_PARAMETERS[116],
                None,
                None,
            ),
            (
                STRANG_PARAMETERS[116],
                None,
                None,
            ),
        ],
    )
    @patch(
        "smhi.strang.Strang._get_and_load_data",
        return_value=[None, None, None],
    )
    @patch("smhi.strang.Strang._build_time_multipoint_url")
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

        if parameter.parameter is None:
            with pytest.raises(NotImplementedError):
                client.get_multipoint(
                    parameter.parameter,
                    valid_time,
                    time_interval,
                )

            return None

        if valid_time is None:
            with pytest.raises(TypeError):
                client.get_multipoint(
                    parameter.parameter,
                    valid_time,
                    time_interval,
                )

            return None
        mock_get_and_load_data.return_value = (
            {"lat": [71], "lon": [-9], "value": [2]},
            False,
            False,
        )
        client.get_multipoint(
            parameter.parameter,
            valid_time,
            time_interval,
        )

        assert client.parameter == parameter
        assert client.valid_time == arrow.get(valid_time).isoformat()
        assert client.time_interval == time_interval
        assert client.multipoint_url == mock_build_time_multipoint_url.return_value

        mock_build_time_multipoint_url.assert_called_once()
        mock_get_and_load_data.assert_called_once()

    @pytest.mark.parametrize(
        "lat, lon, parameter",
        [
            (
                None,
                None,
                STRANG(
                    None,
                    None,
                    None,
                    None,
                ),
            ),
            (
                "16",
                "50",
                STRANG_PARAMETERS[116],
            ),
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
        client.longitude = lon
        client.latitude = lat
        client.parameter = parameter

        url = partial(STRANG_POINT_URL.format, category=CATEGORY, version=VERSION)
        url = url(lon=lon, lat=lat, parameter=parameter.parameter)

        base_url = client._build_base_point_url(client.point_raw_url)

        assert base_url == url

    @pytest.mark.parametrize(
        "parameter, valid_time",
        [
            (
                STRANG(
                    None,
                    None,
                    None,
                    None,
                ),
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
        client.parameter = parameter
        client.valid_time = valid_time

        url = partial(STRANG_MULTIPOINT_URL.format, category=CATEGORY, version=VERSION)
        url = url(parameter=parameter.parameter, validtime=valid_time)

        base_url = client._build_base_multipoint_url(client.multipoint_raw_url)

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

        client.time_from = time_from
        client.time_to = time_to
        client.time_interval = time_interval
        client.url = "URL"

        if time_interval == "bad":
            with pytest.raises(ValueError):
                client._build_time_point_url(client.url)
        elif time_interval == "notimplemented":
            with pytest.raises(NotImplementedError):
                client._build_time_point_url(client.url)
        else:
            assert expected_url == client._build_time_point_url(client.url)

    @pytest.mark.parametrize(
        "time_interval, expected_url",
        [
            (None, "URL"),
            (
                "hourly",
                "URL?interval=hourly",
            ),
            ("notimplemented", None),
        ],
    )
    def test_unit_strang_build_time_multipoint_url(self, time_interval, expected_url):
        """Unit test for Strang _build_time_multipoint_url method.

        Args:
            time_interval: interval of date
            expected_url: expected URL
        """
        client = Strang()

        client.time_interval = time_interval
        client.url = "URL"

        if time_interval == "notimplemented":
            with pytest.raises(ValueError):
                client._build_time_multipoint_url(client.url)
        else:
            assert expected_url == client._build_time_multipoint_url(client.url)

    @pytest.mark.parametrize(
        "ok, date_time",
        [
            (True, [{"date_time": "2020-01-01T00:00:00Z"}]),
            (False, [{"date_time": "2020-01-01T00:00:00Z"}]),
        ],
    )
    @patch("smhi.strang.logging.info")
    @patch(
        "smhi.strang.requests.get",
        return_value=type(
            "MyClass",
            (object,),
            {"ok": True, "headers": "header", "content": "content"},
        )(),
    )
    @patch(
        "smhi.strang.json.loads", return_value=[{"date_time": "2020-01-01T00:00:00Z"}]
    )
    def test_unit_strang_get_and_load_data(
        self, mock_json_loads, mock_requests_get, mock_logging, ok, date_time
    ):
        """Unit test for Strang Point get_and_load_strang_data method.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
            mock_logging: mock of logging warning method
            ok: request status
            date_time: date
        """
        client = Strang()
        client.url = "URL"
        mock_json_loads.return_value = date_time
        mock_requests_get.return_value.ok = ok
        data, headers, status = client._get_and_load_data(client.url)
        mock_requests_get.assert_called_once_with(client.url)

        if ok is True:
            mock_json_loads.assert_called_once_with(
                mock_requests_get.return_value.content
            )
            assert status is ok
            assert headers == "header"
            assert data[0]["date_time"] == arrow.get("2020-01-01T00:00:00Z").datetime
            mock_logging.assert_not_called()

        else:
            assert status is ok
            assert headers == "header"
            assert data == []
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
        client.parameter = parameter

        if date_time == "Q" or date_time == "1900":
            with pytest.raises(ValueError):
                client._parse_datetime(date_time)
        else:
            assert client._parse_datetime(date_time) == expected
