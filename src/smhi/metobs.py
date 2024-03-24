"""SMHI Metobs client."""

import io
import logging
from collections import namedtuple
from typing import Any, Optional, TypeAlias, Union

import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
from smhi.constants import METOBS_AVAILABLE_PERIODS, TYPE_MAP
from smhi.models.metobs_data import DataModel
from smhi.models.metobs_parameters import ParameterItem, ParameterModel
from smhi.models.metobs_periods import PeriodModel
from smhi.models.metobs_stations import StationModel
from smhi.models.metobs_versions import VersionModel

MetobsData = namedtuple("MetobsData", "station, parameter, period, stationdata")
MetobsModels: TypeAlias = (
    VersionModel | ParameterModel | StationModel | PeriodModel | DataModel
)

logger = logging.getLogger(__name__)


class BaseMetobs:
    """Base Metobs class."""

    def __init__(self) -> None:
        """Initialise base class."""
        self.headers: Optional[CaseInsensitiveDict] = None
        self.key: Optional[str] = None
        self.updated: Optional[int] = None
        self.title: Optional[str] = None
        self.summary: Optional[str] = None
        self.link: Optional[str] = None

    def _get_and_parse_request(self, url: str, model: MetobsModels) -> MetobsModels:
        """Get and parse API request. Only JSON supported.

        Args:
            url: url to get from
            model: pydantic model to populate

        Returns:
            pydantic model

        Raise:
            requests.exceptions.HTTPError
        """
        logger.info(f"Fetching from {url} for model {model}.")

        response = requests.get(url, timeout=200)
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(
                f"Could not find or load from given URL: {url}."
            )

        model = model.model_validate_json(response.content)

        self.headers = response.headers
        self.key = model.key
        self.updated = model.updated
        self.title = model.title
        self.summary = model.summary
        self.link = model.link

        return model

    def _get_url(
        self,
        data: list[Any],
        key: str,
        parameter: Union[str, int],
        data_type: str = "json",
    ) -> tuple[str, str]:
        """Get the url to get data from. Defaults to type json.

        Args:
            data: data list
            key: key to look up
            parameter: parameter to look for
            data_type: data type of requested url

        Returns:
            url
            summary

        Raises:
            IndexError
        """
        self.data_type = TYPE_MAP[data_type]
        try:
            requested_data = [x for x in data if getattr(x, key) == str(parameter)][0]
            url = [x.href for x in requested_data.link if x.type == self.data_type][0]
            summary = requested_data.summary
            return url, summary
        except IndexError:
            raise IndexError("Can't find data for parameters: {p}".format(p=parameter))
        except TypeError:
            raise TypeError("Can't find field: {key}".format(key=key))


class Versions(BaseMetobs):
    """Get available versions of Metobs API."""

    def __init__(
        self,
        data_type: str = "json",
    ) -> None:
        """Get versions.

        For now, only supports `json` and version 1.

        Args:
            data_type: data_type of request

        Raises:
            TypeError: data_type not supported
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        self.base_url = f"https://opendata-download-metobs.smhi.se/api.{data_type}"

        model = self._get_and_parse_request(self.base_url, VersionModel)

        self.data = model.version


class Parameters(BaseMetobs):
    """Get parameters for version 1 of Metobs API."""

    def __init__(
        self,
        versions_object: Optional[Versions] = None,
        version: Union[str, int] = "1.0",
        data_type: str = "json",
    ) -> None:
        """Get parameters from version.

        Args:
            versions_object: versions object
            version: selected version
            data_type: data_type of request

        Raises:
            TypeError: data_type not supported
            NotImplementedError: version not implemented
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        version = "1.0" if version == 1 else version
        if version != "1.0":
            raise NotImplementedError("Only supports version 1.0.")

        if versions_object is None:
            versions_object = Versions()

        url, _ = self._get_url(versions_object.data, "key", version, data_type)
        model = self._get_and_parse_request(url, ParameterModel)

        self.versions_object = versions_object
        self.selected_version = version
        self.resource = model.resource
        self.data = tuple(
            ParameterItem(
                key=x.key,
                title=x.title,
                summary=x.summary,
                unit=x.unit,
                updated=x.updated,
                geo_box=x.geo_box,
            )
            for x in self.resource
        )


class Stations(BaseMetobs):
    """Get stations from parameter for version 1 of Metobs API."""

    def __init__(
        self,
        parameters_in_version: Parameters,
        parameter: Optional[int] = None,
        parameter_title: Optional[str] = None,
        data_type: str = "json",
    ) -> None:
        """Get stations from parameters.

        Args:
            parameters_in_version: parameters object
            parameter: integer parameter key to get
            parameter_title: exact parameter title to get
            data_type: data_type of request

        Raises:
            TypeError: data_type not supported
            NotImplementedError: parameter not implemented
        """
        super().__init__()
        self.selected_parameter: Optional[Union[int, str]] = None

        if data_type != "json":
            raise TypeError("Only json supported.")

        if parameter is None and parameter_title is None:
            raise NotImplementedError("No parameter selected.")

        if parameter and parameter_title:
            raise NotImplementedError("Can't decide which input to select.")

        self.parameters_in_version = parameters_in_version
        if parameter:
            self.selected_parameter = parameter
            url, _ = self._get_url(
                parameters_in_version.resource, "key", parameter, data_type
            )
        if parameter_title:
            self.selected_parameter = parameter_title
            url, _ = self._get_url(
                parameters_in_version.resource, "title", parameter_title, data_type
            )

        model = self._get_and_parse_request(url, StationModel)

        self.valuetype = model.value_type
        self.stationset = model.station_set
        self.stations = model.station
        self.data = tuple((x.id, x.name) for x in self.stations)


class Periods(BaseMetobs):
    """Get periods from station for version 1 of Metobs API.

    Note that stationset_title is not supported
    """

    def __init__(
        self,
        stations_in_parameter: Stations,
        station: Optional[int] = None,
        station_name: Optional[str] = None,
        stationset: Optional[str] = None,
        data_type: str = "json",
    ) -> None:
        """Get periods from station.

        Args:
            stations_in_parameter: stations object
            station: integer station key to get
            station_name: exact station name to get
            stationset: station set to get
            data_type: data_type of request

        Raises:
            TypeError: data_type not supported
            NotImplementedError: station not implemented
        """
        super().__init__()
        self.selected_station: Optional[Union[int, str]] = None

        if data_type != "json":
            raise TypeError("Only json supported.")

        if [station, station_name, stationset].count(None) == 3:
            raise NotImplementedError("No stations selected.")

        if [bool(x) for x in [station, station_name, stationset]].count(True) > 1:
            raise NotImplementedError("Can't decide which input to select.")

        self.stations_in_parameter = stations_in_parameter
        if station:
            self.selected_station = station
            url, _ = self._get_url(
                stations_in_parameter.stations, "key", station, data_type
            )
        if station_name:
            self.selected_station = station_name
            url, _ = self._get_url(
                stations_in_parameter.stations, "name", station_name, data_type
            )
        if stationset:
            self.selected_station = stationset
            url, _ = self._get_url(
                stations_in_parameter.stations, "key", stationset, data_type
            )

        model = self._get_and_parse_request(url, PeriodModel)

        self.owner = model.owner
        self.ownercategory = model.owner_category
        self.measuringstations = model.measuring_stations
        self.active = model.active
        self.time_from = model.from_
        self.time_to = model.to
        self.position = model.position
        self.periods = model.period
        self.data = tuple(x.key for x in self.periods)


class Data(BaseMetobs):
    """Get data from period for version 1 of Metobs API."""

    metobs_available_periods = METOBS_AVAILABLE_PERIODS
    metobs_parameter_tim = ["Datum", "Tid (UTC)"]
    metobs_parameter_dygn = ["Representativt dygn"]
    metobs_parameter_manad = ["Representativ månad"]

    def __init__(
        self,
        periods_in_station: Periods,
        period: str = "corrected-archive",
        data_type: str = "json",
    ) -> None:
        """Get data from period.

        Args:
            periods_in_station: periods object
            period: select period from:
                    latest-hour, latest-day, latest-months or corrected-archive
            data_type: data_type of request

        Raises:
            TypeError: data_type not supported
            NotImplementedError: period not implemented
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        if period not in self.metobs_available_periods:
            raise NotImplementedError(
                "Select a supported periods: }"
                + ", ".join([p for p in self.metobs_available_periods])
            )

        self.periods_in_station = periods_in_station
        self.selected_period = period

        url, _ = self._get_url(periods_in_station.periods, "key", period, data_type)
        model = self._get_and_parse_request(url, DataModel)

        self.time_from = model.from_
        self.time_to = model.to
        self.raw_data = model.data

        data_model = self._get_data()

        self.station = data_model.station
        self.parameter = data_model.parameter
        self.period = data_model.period
        self.data = self._set_dataframe_index(data_model.stationdata)

    def _get_data(self, type: str = "text/plain") -> MetobsData:
        """Get the selected data file.

        Args:
            type: type of request
        """
        link = [
            link.href
            for item in self.raw_data
            for link in item.link
            if link.type == type
        ]

        if len(link) == 0:
            raise NotImplementedError("Can't find CSV file to download.")
        if len(link) > 1:
            raise NotImplementedError(
                "Found several CSV files to download, this is currently not supported."
            )

        csv_content = requests.get(link[0]).content.split("\n\n")
        return MetobsData(
            *[
                pd.read_csv(io.StringIO(raw_data), sep=";", on_bad_lines="skip")
                for raw_data in csv_content
            ]
        )

    def _set_dataframe_index(self, stationdata: pd.DataFrame) -> pd.DataFrame:
        """Set dataframe index based on datetime column.

        Args:
            data: station dataframe

        Returns:
            return augmented dataframe

        Raise:
            TypeError
        """
        columns = stationdata.columns
        if any([c for c in self.metobs_parameter_tim if c in columns]):
            datetime_columns = self.metobs_parameter_tim
        elif any([c for c in self.metobs_parameter_dygn if c in columns]):
            datetime_columns = self.metobs_parameter_dygn
        elif any([c for c in self.metobs_parameter_manad if c in columns]):
            datetime_columns = self.metobs_parameter_manad
        else:
            raise TypeError("Can't parse type.")

        stationdata.set_index(
            pd.to_datetime(stationdata[datetime_columns].agg(" ".join, axis=1)),
            inplace=True,
        )
        stationdata.drop(datetime_columns, axis=1, inplace=True)

        return stationdata
