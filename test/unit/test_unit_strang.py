"""
SMHI unit tests.
"""
import arrow
import pytest
from datetime import datetime
from functools import partial
from unittest.mock import patch
from smhi.strang import Strang
from smhi.constants import (
    STRANG,
    STRANG_POINT_URL,
    STRANG_PARAMETERS,
)


CATEGORY = "strang1g"
VERSION = 1


class TestUnitStrang:
    """
    Unit tests for STRÅNG Point class.
    """

    def test_unit_strang_point_init(self):
        """
        Unit test for STRÅNG Point init method.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
        """
        client = Strang()

        assert client._category == CATEGORY
        assert client._version == VERSION

        assert client.latitude is None
        assert client.longitude is None
        assert client.parameter is None
        assert client.status is None
        assert client.header is None
        assert client.data is None
        assert client.available_parameters == STRANG_PARAMETERS

        raw_url_dict = {"category": CATEGORY, "version": VERSION}
        for k1, k2 in zip(
            sorted(raw_url_dict.keys()), sorted(client.raw_url.keywords.keys())
        ):
            assert k1 == k2
            assert raw_url_dict[k1] == client.raw_url.keywords[k2]

        assert client.url is None

    def test_unit_strang_point_parameters(self):
        """
        Unit test for STRÅNG Point parameters get property.
        """
        client = Strang()
        assert client.parameters == STRANG_PARAMETERS

    @pytest.mark.parametrize(
        "lon, lat, parameter, time_from, time_to, time_interval",
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
        "smhi.strang.Strang._fetch_and_load_point_data",
        return_value=[None, None, None],
    )
    @patch("smhi.strang.Strang._build_date_url")
    def test_unit_strang_point_fetch_point(
        self,
        mock_build_date_url,
        mock_fetch_and_load_point_data,
        lon,
        lat,
        parameter,
        time_from,
        time_to,
        time_interval,
    ):
        """
        Unit test for STRÅNG Point fetch_point method.

        Args:
            mock_build_date_url: mock _build_date_url method
            mock_fetch_and_load_point_data: mock _fetch_and_load_point_data method
            lon: longitude
            lat: latitude
            parameter: parameter
            time_from: from time
            time_to: to time
            time_interval: time interval
        """
        client = Strang()

        if parameter.parameter is None:
            with pytest.raises(NotImplementedError):
                client.fetch_point(
                    lon,
                    lat,
                    parameter.parameter,
                    time_from,
                    time_to,
                    time_interval,
                )

            return None

        if lon is None:
            mock_fetch_and_load_point_data.return_value[0] = False
            with pytest.raises(ValueError):
                client.fetch_point(
                    lon,
                    lat,
                    parameter.parameter,
                    time_from,
                    time_to,
                    time_interval,
                )

            return None

        client.fetch_point(
            lon,
            lat,
            parameter.parameter,
            time_from,
            time_to,
            time_interval,
        )

        assert client.longitude == lon
        assert client.latitude == lat
        assert client.parameter == parameter
        assert client.url == mock_build_date_url.return_value

        mock_build_date_url.assert_called_once()
        mock_fetch_and_load_point_data.assert_called_once()

    @pytest.mark.parametrize(
        "lon, lat, parameter",
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
                "50",
                "16",
                STRANG_PARAMETERS[116],
            ),
        ],
    )
    def test_unit_strang_point_build_base_url(self, lon, lat, parameter):
        """
        Unit test for STRANG Point _build_base_url method

        Args:
            lon: longitude
            lat: latitude
            parameter: parmeter
        """
        client = Strang()
        client.longitude = lon
        client.latitude = lat
        client.parameter = parameter

        url = partial(STRANG_POINT_URL.format, category=CATEGORY, version=VERSION)
        url = url(lon=lon, lat=lat, parameter=parameter.parameter)

        client._build_base_url()

        assert client.url == url

    @pytest.mark.parametrize(
        "date_from, date_to, date_interval, expected_url",
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
    @patch("smhi.strang.Strang._parse_date")
    def test_unit_strang_point_build_date_url(
        self, mock_parse_date, date_from, date_to, date_interval, expected_url
    ):
        """
        Unit test for STRANG Point _build_date_url method

        Args:
            mock_parse_date: mock of _parse_date method
            date_from: from date
            date_to: to date
            date_interval: interval of date
            expected_url: expected URL
        """
        client = Strang()
        mock_parse_date.side_effect = [date_from, date_to]

        client.date_from = date_from
        client.date_to = date_to
        client.date_interval = date_interval
        client.url = "URL"

        if date_interval == "bad":
            with pytest.raises(ValueError):
                client._build_date_url()
        elif date_interval == "notimplemented":
            with pytest.raises(NotImplementedError):
                client._build_date_url()
        else:
            assert expected_url == client._build_date_url()

    @pytest.mark.parametrize(
        "ok, date_time",
        [
            (True, [{"date_time": "2020-01-01T00:00:00Z"}]),
            (False, [{"date_time": "2020-01-01T00:00:00Z"}]),
        ],
    )
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
    def test_unit_strang_point_fetch_and_load_point_data(
        self, mock_json_loads, mock_requests_get, ok, date_time
    ):
        """
        Unit test for STRANG Point fetch_and_load_strang_data method.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
            ok: request status
            date_time: date
        """
        client = Strang()
        client.url = "URL"
        mock_json_loads.return_value = date_time
        mock_requests_get.return_value.ok = ok
        status, headers, data = client._fetch_and_load_point_data()
        mock_requests_get.assert_called_once_with(client.url)

        if ok is True:
            mock_json_loads.assert_called_once_with(
                mock_requests_get.return_value.content
            )
            assert status is ok
            assert headers == "header"
            assert data[0]["date_time"] == arrow.get("2020-01-01T00:00:00Z").datetime

        else:
            assert status is ok
            assert headers == "header"
            assert data is None

    @pytest.mark.parametrize(
        "parameter, date, expected",
        [
            (STRANG_PARAMETERS[0], None, None),
            (STRANG_PARAMETERS[0], "Q", None),
            (STRANG_PARAMETERS[116], "1900", None),
            (STRANG_PARAMETERS[116], "2000", arrow.get("2000").datetime),
        ],
    )
    def test_unit_strang_point_parse_date(self, parameter, date, expected):
        """
        Unit test for STRANG Point _parse_date method.

        Args:
            parameter: selected parameter
            date: input data to parse
            expected: expected result
        """
        client = Strang()
        client.parameter = parameter

        if date == "Q" or date == "1900":
            with pytest.raises(ValueError):
                client._parse_date(date)
        else:
            assert client._parse_date(date) == expected
