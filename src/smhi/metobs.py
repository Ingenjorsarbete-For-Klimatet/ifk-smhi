"""SMHI Metobs client."""

import io
import logging
import requests
import pandas as pd
from typing import Union, Optional, Any
from requests.structures import CaseInsensitiveDict
from smhi.constants import (
    TYPE_MAP,
    METOBS_AVAILABLE_PERIODS,
    METOBS_PARAMETER_TIM,
    METOBS_PARAMETER_DYGN,
    METOBS_PARAMETER_MANAD,
)

from smhi.models.metobs_versions import VersionModel
from smhi.models.metobs_parameters import ParameterModel
from smhi.models.metobs_stations import StationModel
from smhi.models.metobs_periods import PeriodModel
from smhi.models.metobs_data import DataModel

MetobsModels = VersionModel | ParameterModel | StationModel | PeriodModel | DataModel


class BaseMetobs:
    """Base Metobs class."""

    headers: CaseInsensitiveDict
    key: str
    updated: int
    title: str
    summary: str
    link: str

    def __init__(self) -> None:
        """Initialise base class."""
        pass

    @property
    def show(self) -> None:
        """Show property."""
        if self.data is None:
            return None

        for item in self.data:
            logging.info(item)

    def _get_and_parse_request(self, url: str, model: MetobsModels) -> MetobsModels:
        """Get and parse API request. Only JSON supported.

        Args:
            url: url to get from
            model: pydantic model to populate

        Returns:
            pydantic model
        """
        response = requests.get(url, timeout=200)
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
        except KeyError:
            raise KeyError("Can't find key: {key}".format(key=key))


class Versions(BaseMetobs):
    """Get available versions of Metobs API."""

    base_url: str = "https://opendata-download-metobs.smhi.se/api.{data_type}"

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

        base_url = self.base_url.format(data_type=data_type)

        model = self._get_and_parse_request(base_url, VersionModel)

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

        self.versions_object = versions_object
        self.selected_version = version

        url, _ = self._get_url(versions_object.data, "key", version, data_type)
        model = self._get_and_parse_request(url, ParameterModel)

        self.resource = sorted(model.resource, key=lambda x: int(x.key))
        self.data = tuple((x.key, x.title, x.summary) for x in self.resource)


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
            url, parameter_summary = self._get_url(
                parameters_in_version.resource, "key", parameter, data_type
            )
        if parameter_title:
            self.selected_parameter = parameter_title
            url, parameter_summary = self._get_url(
                parameters_in_version.resource, "title", parameter_title, data_type
            )

        self.parameter_summary = parameter_summary

        model = self._get_and_parse_request(url, StationModel)

        self.valuetype = model.valueType
        self.stationset = model.stationSet
        self.stations = sorted(model.station, key=lambda x: int(x.id))
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
        self.parameter_summary = stations_in_parameter.parameter_summary

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

        content = self._get_and_parse_request(url, PeriodModel)

        self.owner = content.owner
        self.ownercategory = content.ownerCategory
        self.measuringstations = content.measuringStations
        self.active = content.active
        self.time_from = content.from_
        self.time_to = content.to
        self.position = content.position
        self.periods = sorted(content.period, key=lambda x: x.key)
        self.data = tuple(x.key for x in self.periods)


class Data(BaseMetobs):
    """Get data from period for version 1 of Metobs API."""

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

        self.parameter_summary = periods_in_station.parameter_summary

        if data_type != "json":
            raise TypeError("Only json supported.")

        if period not in METOBS_AVAILABLE_PERIODS:
            raise NotImplementedError(
                "Select a supported periods: }"
                + ", ".join([p for p in METOBS_AVAILABLE_PERIODS])
            )

        self.periods_in_station = periods_in_station
        self.selected_period = period

        url, _ = self._get_url(periods_in_station.periods, "key", period, data_type)
        content = self._get_and_parse_request(url, DataModel)

        self.time_from = content.from_
        self.time_to = content.to
        self.raw_data = content.data
        self._get_data()

    def _get_data(self, type: str = "text/plain") -> None:
        """Get the selected data file.

        Args:
            type: type of request
        """
        for item in self.raw_data:
            for link in item.link:
                if link.type != type:
                    continue

                content = requests.get(link.href).content.decode("utf-8")
                raw_data_header, raw_data = self._separate_header_data(content)
                self._parse_header(raw_data_header)
                self._parse_data(raw_data)
                return

    def _separate_header_data(self, content: str) -> tuple:
        """Separate header and data into two strings.

        Args:
            content: raw data string
        """
        data_starting_point = content.find("Datum")
        self.raw_data_header = content[:data_starting_point]
        self.raw_data = content[data_starting_point:-1]

        return self.raw_data_header, self.raw_data

    def _parse_header(self, raw_data_header: str) -> None:
        """Parse header string.

        Args:
            raw_data_header: raw data header as a string
        """
        data_headers = []
        for header in raw_data_header.split("\n\n")[:-1]:
            try:
                data_headers.append(
                    pd.read_csv(
                        io.StringIO(header),
                        sep=";",
                        on_bad_lines="skip",
                    ).to_dict("records")[0]
                )
            except pd.errors.EmptyDataError:
                logging.warning("No columns to parse.")

        self.data_header = {k: v for d in data_headers for k, v in d.items()}

    def _parse_data(self, raw_data: str) -> None:
        """Parse string data.

        Args:
            raw_data: utf-8 decoded response

        Raises:
            NotImplementedError
        """
        self.data = pd.read_csv(
            io.StringIO(raw_data),
            sep=";",
            on_bad_lines="skip",
            usecols=[0, 1, 2, 3],
        )
        columns = self.data.columns

        if any([c for c in METOBS_PARAMETER_TIM if c in columns]):
            datetime_columns = METOBS_PARAMETER_TIM
        elif any([c for c in METOBS_PARAMETER_DYGN if c in columns]):
            datetime_columns = METOBS_PARAMETER_DYGN
        elif any([c for c in METOBS_PARAMETER_MANAD if c in columns]):
            datetime_columns = METOBS_PARAMETER_MANAD
        else:
            raise TypeError("Can't parse type.")

        try:
            self.data.set_index(
                pd.to_datetime(self.data[datetime_columns].agg(" ".join, axis=1)),
                inplace=True,
            )
            self.data.drop(datetime_columns, axis=1, inplace=True)
        except TypeError:
            raise TypeError("Can't parse date of empty data.")
