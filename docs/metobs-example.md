# Example of Metobs direct use

Direct usage of `Metobs`.

## Basic chain

The `Metobs` client consistes of 5 objects
`Versions, Parameters, Stations, Periods, Data`
that building up a chain to get data.

```python
from smhi.metobs import Versions, Parameters, Stations, Periods, Data

versions = Versions()  # defaults to type = json, this step can be skipped
versions.data
# show data from this endpoint

parameters = Parameters(versions)  # can be called: Parameters()
parameters.data
# show all available parameters in that API version

stations = Stations(parameters, 1)
stations.data
# show all available stations for parameter 1

periods = Periods(stations, 1)
periods.data
# show all available periods of data for station 1

data = Data(periods)  # defaults to corrected-archive period
data.df
# show the station data dataframe
```

The `data` variable holds four dataframes when a single station
is used to fetch data as above.
They are called `station`, `parameter`, `period` and `df`.

It is posible to fetch a station set, that is, data from many stations for
the last hour as

```python
periods = Periods(stations, station_set="all")
periods.data
# show all available periods of data for station set all

data = Data(periods)  # defaults to corrected-archive period
data.df
# show
```

in which case only the `parameter` and `df` fields are populated.

## Detailed chain

All objects contain several useful fields, in this example we will
look at a few of them. For a full reference see
[Metobs reference](/ifk-smhi/metobs-reference/).

### All objects

All objects contain these fields

- `headers`
- `key`
- `updated`
- `title`
- `summary`
- `link`
- `url`

```python
from smhi.metobs import Versions

versions = Versions()
versions.headers
# show response header

versions.title
# show API title

versions.link
# show list of links subsequent APIs will use

versions.url
# the URL used for the request
```

### Parameters

The most important fields are

- `resource`
- `data`

where `data` is equal to `resource`, but condensed in information.

```python
from smhi.metobs import Parameters

parameters = Parameters()
parameters.data
# tuple of parameters with key, title, summary and unit fields

parameters.data
# list of parameters with all available fields
```

### Stations

The most important fields are

- `station`
- `station_set`
- `data`

where again `data` is equal to `station`, but condensed in information.
`station_set` is entirely different here.

It is important to note that parameter key `1` in the example below also has
name `Lufttemperatur` and this object can be called with both.

```python
from smhi.metobs import Stations

stations = Stations(parameters, 1)
stations = Stations(parameters, parameter_title="Lufttemperatur") # equivalent
stations.data
# tuple of stations with a tuple containing station id and name

stations.station
# list of stations with all available fields

stations.station_set
# list of station sets
```

### Periods

The most important fields are

- `period`
- `data`
- `position`
- `owner`
- `active`
- `time_from`
- `time_to`

where again `data` is equal to `period`, but condensed in information.

Note that, `Periods` can be called with a station `id=1`, `name="Akalla"`
(from the above station) or `station_set="all"` key.

```python
from smhi.metobs import Periods

periods = Periods(stations, 1)
periods = Periods(stations, station_name="Akalla") # equivalent

periods.data
# tuple of available periods, e.g. "corrected-archive" etc.

periods.period
# list of all available information for periods available

periods.position
# list station position, height, latitude and longitude

periods.owner
# station owner

periods.active
# boolean whether the station is active or not

periods.time_from
# datetime from when the station started collecting data

periods.time_to
# datetime until when the station collected data
```

When `Periods` is called with `station_set` many fields are empty.

```python
from smhi.metobs import Periods

periods_set = Periods(stations, station_set="all") # not equivalent to above

periods_set.data
# tuple of available periods, e.g. "corrected-archive" etc.

periods_set.period
# list of all available information for periods available

periods_set.position
periods_set.owner
periods_set.active
periods_set.time_from
periods_set.time_to
# all empty as data response will contain data from many stations
```

### Data from station

Finally, we can fetch the actual data. The most important fields are

- `df`
- `parameter`
- `station`
- `period`
- `time_from`
- `time_to`

```python
from smhi.metobs import Data

data = Data(periods, period="corrected-archive") # period can be omitted

data.df
# dataframe of actual data

data.parameter
# dataframe with parameter information, e.g. units and frequency

data.station
# dataframe with station information

data.period
# dataframe with period and location information

data.time_from
# datetime from when data is available in response

data.time_to
# datetime until data is available in response
```

### Data from station set

Data from a station set is slighlty different and the most important fields are

- `df`
- `station`
- `time_from`
- `time_to`

```python
from smhi.metobs import Data

data = Data(periods_set)

data.df
# dataframe of actual data

data.parameter
# dataframe with parameter information, e.g. units and frequency

data.station
data.period
# empty, reponse contains data from many stations

data.time_from
# datetime from when data is available in response

data.time_to
# datetime until data is available in response
```
