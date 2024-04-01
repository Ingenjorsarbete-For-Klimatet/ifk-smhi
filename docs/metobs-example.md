# Example of Metobs direct use

Direct usage of `Metobs`.

The `Metobs` clinet consistes of 5 objects
`Versions, Parameters, Stations, Periods, Data`
that building up a chain to get data.

```python
from smhi.metobs import Versions, Parameters, Stations, Periods, Data

versions = Versions()  # defaults to type = json, this step can be skipped
versions.data
# show data from this endpoint

parameters = Parameters(versions)  # can be called by simply Parameters()
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

Note that, the last call gives back a `MetobsDataModel` with four
dataframes when a single station is used to fetch data as above.
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
