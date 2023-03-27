# Example of Metobs direct use

Direct usage of `Metobs`.

## Get data from known parameters

To get data from a known station (found e.g. through exploration of
[https://www.smhi.se/data](https://www.smhi.se/data)) from `Metobs` do

```python
from smhi.metobs import Metobs

client = Metobs()
data = client.get_data_stationset(
    1, 192840, "corrected-archive"
)
```

## Get data by inspecting the API

*This will be deprecated in 0.2.0.*
To inspect the API, the following methods are provided
The following example is a common pattern of usage

```python
from smhi.metobs import Metobs

client = Metobs()
client.get_parameters()

# list all parameters
client.parameters.data

# get all stations that have data from parameter 1
client.get_stations(1)

# list all stations
client.stations.data

# get all periods that have data from station 1
client.get_periods(1)

# list all periods
client.periods.data

# inspect client state
client.inspect()

# get data from parameter 1, station 1 and period corrected-archive
data = client.get_data()
```

## Alternative way of using the client

Instead of using the `Metobs` client, the objects used by that client can be
used directly. The following example is a recommended pattern of usage

```python
from smhi.metobs import Versions, Parameters, Stations, Periods, Data

versions = Versions()  # defaults to type = json, this step can be skipped
versions.show
# print all available versions

parameters = Parameters(versions)  # can be called by simply Parameters()
parameters.show
# print all available parameters in that API version

stations = Stations(parameters, 1)
stations.show
# print all available stations for parameter 1

periods = Periods(stations, 1)
periods.show
# print all available periods of data for station 1

data = Data(periods)  # defaults to corrected-archive period
data.data_header  # data headers
data.data  # actual data
```
