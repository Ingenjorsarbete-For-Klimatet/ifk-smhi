"""
SMHI unit tests.
"""
import pytest
from unittest.mock import patch
from smhi.strang import Strang, check_date_validity, fetch_and_load_strang_data
from functools import partial
from smhi.constants import (
    STRANG,
    STRANG_URL,
    STRANG_URL_TIME,
    STRANG_PARAMETERS,
    STRANG_DATE_FORMAT,
    STRANG_DATETIME_FORMAT,
    STRANG_TIME_INTERVALS,
)


CATEGORY = "strang1g"
VERSION = 1


class TestUnitStrang:
    """
    Unit tests for STRÅNG class.
    """

    def test_unit_strang_init(self):
        """
        Unit test for STRÅNG init method.

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

        assert (
            all(
                [x == y for x, y in zip(client.available_parameters, STRANG_PARAMETERS)]
            )
            is True
        )

        raw_url_dict = {"category": CATEGORY, "version": VERSION}
        for k1, k2 in zip(
            sorted(raw_url_dict.keys()), sorted(client.raw_url.keywords.keys())
        ):
            assert k1 == k2
            assert raw_url_dict[k1] == client.raw_url.keywords[k2]

        assert client.time_url is STRANG_URL_TIME
        assert client.url is None

    def test_unit_strang_parameters(self):
        """
        Unit test for STRÅNG parameters get property.
        """
        client = Strang()
        assert (
            all(
                [x == y for x, y in zip(client.available_parameters, STRANG_PARAMETERS)]
            )
            is True
        )

    @pytest.mark.parametrize(
        "lon, lat, parameter, time_from, time_to, time_interval",
        [
            (0, 0, 0, "2020-01-01", "2020-01-01", "hourly"),
            (116, 0, 0, None, None, None),
            (116, 0, 0, "2020-01-01", "2020-01-01", "hourly"),
        ],
    )
    @patch("smhi.strang.check_date_validity")
    @patch("smhi.strang.fetch_and_load_strang_data")
    def test_unit_strang_fetch_data(
        self,
        mock_check_date_validity,
        mock_fetch_and_load_strang_data,
        lon,
        lat,
        parameter,
        time_from,
        time_to,
        time_interval,
    ):
        """
        Unit test for STRÅNG fetch_data method.

        Args:
            mock_check_date_validity: mock check_date_validity method
            mock_fetch_and_load_strang_data: mock fetch_and_load_strang_data method
            lon: longitude
            lat: latitude
            parameter: parameter
            time_from: from time
            time_to: to time
            time_interval: time interval
        """
        client = Strang()
        url = STRANG_URL
        time_url = STRANG_URL_TIME

        if parameter == 0:
            with pytest.raises(NotImplementedError):
                client.fetch_data(
                    lon,
                    lat,
                    parameter,
                    time_from,
                    time_to,
                    time_interval,
                )
        else:
            client.fetch_data(
                lon,
                lat,
                parameter,
                time_from,
                time_to,
                time_interval,
            )

            assert client.longitude == lon
            assert client.latitude == lat
            assert (
                client.parameter
                == [p for p in self.available_parameters if p.parameter == parameter][0]
            )

            url_dict = {"lon": lon, "lat": lat, "parameter": parameter.parameter}
            for k1, k2 in zip(
                sorted(url_dict.keys()), sorted(client.url.keywords.keys())
            ):
                assert k1 == k2
                assert url_dict[k1] == client.url.keywords[k2]

            if time_from is not None:
                mock_check_date_validity.assert_called_once_with(
                    parameter,
                    url,
                    time_url,
                    time_from,
                    time_to,
                    time_interval,
                )
            mock_fetch_and_load_strang_data.assert_called_once_with(url)

    def test_unit_strang_check_date_validity(self):
        """
        Unit test for STRANG check_date_validity function, type error and interval error.
        """
        parameter = STRANG_PARAMETERS[0]
        url = "URL"
        time_url = "URL_TIME"

        with pytest.raises(TypeError):
            time_from = "2020-01-01"
            time_to = None
            time_interval = "hourly"
            check_date_validity(
                parameter, url, time_url, time_from, time_to, time_interval
            )

        with pytest.raises(ValueError):
            time_from = "2020-01-01"
            time_to = "2022-01-01"
            time_interval = "minutly"
            check_date_validity(
                parameter, url, time_url, time_from, time_to, time_interval
            )

    @pytest.mark.parametrize(
        "time_from, time_to",
        [
            ("20222-01-01", "2022-01-01"),
            ("2022-012-01", "2022-01-01"),
            ("2022-01-012", "2022-01-01"),
            ("2022-01-01", "20222-01-01"),
            ("2022-01-01", "2022-012-01"),
            ("2022-01-01", "2022-01-012"),
            ("1900-01-01", "2022-01-01"),
            ("2010-01-01", "3000-01-01"),
            ("2010-01-01", "1900-01-01"),
            ("3000-01-01", "2022-01-01"),
        ],
    )
    def test_unit_strang_check_date_validity_valueerror(self, time_from, time_to):
        """
        Unit test for STRANG check_date_validity function, value error, bounds and format.

        Args:
            time_from: time from
            time_to: time to
        """
        parameter = STRANG_PARAMETERS[0]
        url = "URL"
        time_url = "URL_TIME"
        time_interval = "hourly"

        with pytest.raises(ValueError):
            check_date_validity(
                parameter, url, time_url, time_from, time_to, time_interval
            )

    def test_unit_strang_check_date_validity_correct(self):
        """
        Unit test for STRANG check_date_validity function, correct input.
        """
        parameter = STRANG_PARAMETERS[0]
        url = "URL"
        time_url = "{time_from} {time_to} {time_interval}"
        time_from = "2020-01-01"
        time_to = "2020-01-02"
        time_interval = "hourly"

        returned_url = check_date_validity(
            parameter, url, time_url, time_from, time_to, time_interval
        )

        assert returned_url == "URL2020-01-01 2020-01-02 hourly"

    @patch("smhi.strang.requests.get")
    @patch("smhi.strang.json.loads")
    def test_unit_strang_fetch_and_load_strang_data(
        self, mock_requests_get, mock_json_loads
    ):
        """
        Unit test for STRANG fetch_and_load_strang_data function.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
        """
        # url = "URL"
        # fetch_and_load_strang_data(url)
        # mock_requests_get.assert_called_once_with(url)
        pass
