"""SMHI Mesan v1 unit tests."""

import json
from unittest.mock import patch

import arrow
import pandas as pd
import pytest
from utils import get_response

from smhi.constants import MESAN_LEVELS_UNIT, MESAN_PARAMETER_DESCRIPTIONS
from smhi.mesan import Mesan
from smhi.models.mesan_model import MesanGeometry, MesanParameter, MesanParameterItem
from smhi.utils import format_datetime

BASE_URL = (
    "https://opendata-download-metanalys.smhi.se/" + "api/category/mesan2g/version/2/"
)

MOCK_MESAN_PARAMETERS = MesanParameter(
    url=BASE_URL + "parameter.json",
    status=200,
    headers={"Date": "Sun, 31 Mar 2024 07:37:51 GMT"},
    parameter=[
        MesanParameterItem(
            name="air_temperature",
            shortName="t",
            description="Air temperature at 2 metres height",
            levelType="hl",
            level=2,
            unit="Cel",
            missingValue=9999,
        ),
        MesanParameterItem(
            name="wind_speed_of_gust",
            shortName="gust",
            description="Wind gusts",
            levelType="hl",
            level=10,
            unit="m/s",
            missingValue=9999,
        ),
    ],
)


@pytest.fixture
def setup_point():
    """Read in Point response."""
    mocked_response = get_response("tests/fixtures/mesan/point.txt")
    mocked_model = json.loads(mocked_response.content)

    mocked_approved_time = arrow.get(mocked_model["createdTime"]).datetime
    mocked_reference_time = arrow.get(mocked_model["referenceTime"]).datetime
    mocked_geometry = MesanGeometry(
        type=mocked_model["geometry"]["type"],
        coordinates=[
            [mocked_model["geometry"]["coordinates"][0]],
            [mocked_model["geometry"]["coordinates"][1]],
        ],
    )
    mocked_data = pd.read_csv("tests/fixtures/mesan/point_data.csv", index_col="times")
    mocked_data.index = pd.to_datetime(mocked_data.index)
    mocked_data.columns.name = "name"

    return (
        mocked_response,
        mocked_approved_time,
        mocked_reference_time,
        mocked_geometry,
        mocked_data,
    )


@pytest.fixture
def setup_multipoint():
    """Read in MultiPoint response."""
    mocked_response = get_response("tests/fixtures/mesan/multipoint.txt")
    mocked_model = json.loads(mocked_response.content)

    mocked_approved_time = arrow.get(mocked_model["createdTime"]).datetime
    mocked_reference_time = arrow.get(mocked_model["referenceTime"]).datetime
    mocked_times = arrow.get(mocked_model["timeSeries"][0]["time"]).datetime
    mocked_data = pd.read_csv("tests/fixtures/mesan/multipoint_data.csv", index_col=0)

    return (
        mocked_response,
        mocked_approved_time,
        mocked_reference_time,
        mocked_times,
        mocked_data,
    )


class TestUnitMesan:
    """Unit tests for Mesan class."""

    @patch("smhi.mesan.Mesan._get_parameters", return_value=MOCK_MESAN_PARAMETERS)
    def test_unit_mesan_init(self, mock_get_parameters):
        """Unit test for Mesan init method."""
        client = Mesan()

        assert client._category == "mesan2g"
        assert client._version == 2
        assert client._base_url == BASE_URL
        assert client._parameters == MOCK_MESAN_PARAMETERS

    @patch("smhi.mesan.Mesan._get_parameters", return_value=MOCK_MESAN_PARAMETERS)
    def test_unit_mesan_parameter_descriptions(self, mock_get_data):
        """Unit test for Mesan parameter_descriptions property."""
        client = Mesan()

        assert client.parameter_descriptions == MESAN_PARAMETER_DESCRIPTIONS

    @patch(
        "smhi.mesan.Mesan._get_data",
        return_value=(
            MOCK_MESAN_PARAMETERS.model_dump(by_alias=True),
            MOCK_MESAN_PARAMETERS.headers,
            MOCK_MESAN_PARAMETERS.status,
        ),
    )
    def test_unit_mesan_parameters(self, mock_get_data):
        """Unit test for Mesan parameters property."""
        client = Mesan()

        mock_get_data.assert_called_once_with(BASE_URL + "parameter.json")
        assert client.parameters == MOCK_MESAN_PARAMETERS

    @patch(
        "smhi.mesan.Mesan._get_data",
        return_value=(
            {
                "createdTime": arrow.get(1).datetime,
                "referenceTime": arrow.get(2).datetime,
            },
            {"head": "head"},
            200,
        ),
    )
    @patch("smhi.mesan.Mesan._get_parameters", return_value=MOCK_MESAN_PARAMETERS)
    def test_unit_mesan_approved_time(self, mock_get_parameters, mock_get_data):
        """Unit test for Mesan approved_time property."""
        client = Mesan()
        data = client.created_time
        url = BASE_URL + "createdtime.json"

        mock_get_data.assert_called_once_with(url)
        assert data.url == url
        assert data.created_time == mock_get_data.return_value[0]["createdTime"]
        assert data.reference_time == mock_get_data.return_value[0]["referenceTime"]
        assert data.headers == mock_get_data.return_value[1]
        assert data.status == mock_get_data.return_value[2]

    @patch(
        "smhi.mesan.Mesan._get_data",
        return_value=(
            {"type": "Polygon", "coordinates": [[[1.0, 2.0]]]},
            {"head": "head"},
            200,
        ),
    )
    @patch("smhi.mesan.Mesan._get_parameters", return_value=MOCK_MESAN_PARAMETERS)
    def test_unit_mesan_geo_polygon(self, mock_get_parameters, mock_get_data):
        """Unit test for Mesan geo_polygon property."""
        client = Mesan()
        data = client.geo_polygon
        url = BASE_URL + "geotype/polygon.json"

        mock_get_data.assert_called_once_with(url)
        assert data.url == url
        assert data.coordinates == mock_get_data.return_value[0]["coordinates"]
        assert data.type_ == mock_get_data.return_value[0]["type"]
        assert data.headers == mock_get_data.return_value[1]
        assert data.status == mock_get_data.return_value[2]

    @pytest.mark.parametrize(
        "downsample, bounded_downsample", [(0, 1), (2, 2), (20, 20), (21, 20)]
    )
    @patch(
        "smhi.mesan.Mesan._get_data",
        return_value=(
            {"type": "MultiPoint", "coordinates": [[1.0, 2.0]]},
            {"head": "head"},
            200,
        ),
    )
    @patch("smhi.mesan.Mesan._get_parameters", return_value=MOCK_MESAN_PARAMETERS)
    def test_unit_mesan_get_geo_multipoint(
        self, mock_get_parameters, mock_get_data, downsample, bounded_downsample
    ):
        """Unit test for Mesan get_geo_multipoint method."""
        client = Mesan()
        data = client.get_geo_multipoint(downsample)
        url = BASE_URL + f"geotype/multipoint.json?downsample={bounded_downsample}"

        mock_get_data.assert_called_once_with(url)
        assert data.url == url
        assert data.coordinates == mock_get_data.return_value[0]["coordinates"]
        assert data.type_ == mock_get_data.return_value[0]["type"]
        assert data.headers == mock_get_data.return_value[1]
        assert data.status == mock_get_data.return_value[2]

    @pytest.mark.parametrize("lat, lon", [(0, 0), (1, 1)])
    @patch("smhi.utils.requests.get")
    @patch("smhi.mesan.Mesan._get_parameters", return_value=MOCK_MESAN_PARAMETERS)
    def test_unit_mesan_get_point(
        self, mock_get_parameters, mock_requests_get, lat, lon, setup_point
    ):
        """Unit test for Mesan get_point method."""
        (
            mock_response,
            expected_approved_time,
            expected_reference_time,
            expected_geometry,
            expected_answer,
        ) = setup_point
        mock_requests_get.return_value = mock_response

        client = Mesan()
        data = client.get_point(lat, lon)
        url = BASE_URL + f"geotype/point/lon/{lon}/lat/{lat}/data.json"

        mock_requests_get.assert_called_once_with(url, timeout=200)
        assert data.latitude == lat
        assert data.longitude == lon
        assert data.url == url
        assert data.created_time == expected_approved_time
        assert data.reference_time == expected_reference_time
        assert data.level_unit == MESAN_LEVELS_UNIT
        assert data.geometry == expected_geometry
        assert data.status == mock_response.status_code
        assert data.headers == mock_response.headers
        data.df = data.df.reindex(sorted(data.df.columns), axis=1).sort_index()
        expected_answer = expected_answer.reindex(
            sorted(expected_answer.columns), axis=1
        ).sort_index()

        pd.testing.assert_frame_equal(
            data.df.astype(float), expected_answer.astype(float)
        )

    @pytest.mark.parametrize(
        "times, parameter, geo, downsample",
        [("2024-03-31T06", "air_temperature", True, 1)],
    )
    @patch("smhi.utils.requests.get")
    @patch("smhi.mesan.Mesan._get_parameters", return_value=MOCK_MESAN_PARAMETERS)
    @patch("smhi.mesan.arrow.now", return_value=arrow.get("2024-03-31T07:14:10Z"))
    def test_unit_mesan_get_multipoint(
        self,
        mock_arrow_now,
        mock_get_parameters,
        mock_requests_get,
        times,
        parameter,
        geo,
        downsample,
        setup_multipoint,
    ):
        """Unit test for Mesan get_multipoint method."""
        (
            mock_response,
            expected_approved_time,
            expected_reference_time,
            expected_times,
            expected_answer,
        ) = setup_multipoint
        mock_requests_get.return_value = mock_response

        client = Mesan()
        data = client.get_multipoint(times, parameter, geo, downsample)
        times = format_datetime(times)

        assert data.parameter == parameter
        assert data.parameter_meaning == MESAN_PARAMETER_DESCRIPTIONS[parameter]
        assert data.geo == geo
        assert data.downsample == downsample
        assert data.url is not None
        assert data.created_time == expected_approved_time
        assert data.reference_time == expected_reference_time
        assert data.times == expected_times
        assert data.status == mock_response.status_code
        assert data.headers == mock_response.headers
        pd.testing.assert_frame_equal(data.df, expected_answer)

    @pytest.mark.parametrize(
        "times, parameter, geo, downsample, expected_answer",
        [
            (
                "2024-03-31T06",
                "air_temperature",
                True,
                1,
                "https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/2/geotype/multipoint/time/20240331T060000Z/parameter/air_temperature/data.json?with-geo=true&downsample=1",
            ),
            (
                "2024-03-31T06",
                "air_temperature",
                True,
                0,
                "https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/2/geotype/multipoint/time/20240331T060000Z/parameter/air_temperature/data.json?with-geo=true&downsample=1",
            ),
            (
                "2024-03-31T06",
                "air_temperature",
                True,
                20,
                "https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/2/geotype/multipoint/time/20240331T060000Z/parameter/air_temperature/data.json?with-geo=true&downsample=20",
            ),
            (
                "2024-03-31T06",
                "air_temperature",
                False,
                21,
                "https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/2/geotype/multipoint/time/20240331T060000Z/parameter/air_temperature/data.json?with-geo=false&downsample=20",
            ),
        ],
    )
    @patch("smhi.mesan.Mesan._get_parameters")
    def test_build_multipoint_url(
        self,
        mock_get_parameters,
        times,
        parameter,
        geo,
        downsample,
        expected_answer,
    ):
        """"""
        client = Mesan()
        assert (
            client._build_multipoint_url(
                times,
                parameter,
                geo,
                downsample,
            )
            == expected_answer
        )

    @pytest.mark.parametrize(
        "test_time, expected_answer",
        [
            ("2024-03-31T07:00:00Z", False),
            ("2024-03-31T06:00:00Z", True),
            ("2024-03-30T07:00:00Z", True),
            ("2024-03-30T06:00:00Z", False),
        ],
    )
    @patch("smhi.mesan.Mesan._get_parameters")
    @patch("smhi.mesan.arrow.now", return_value=arrow.get("2024-03-31T07:14:10Z"))
    def test_check_times(
        self, mock_arrow_now, mock_get_parameters, test_time, expected_answer
    ):
        """Unit test _ceck_times."""
        client = Mesan()
        assert client._check_times(test_time) is expected_answer
