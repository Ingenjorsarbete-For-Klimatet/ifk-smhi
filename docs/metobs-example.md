# Example of MetObs direct use

Direct usage of `MetObs`, without using the `SMHI` client is possible.

## Get data from known parameters

To get data from a known station (found e.g. through exploration of
[https://www.smhi.se/data](https://www.smhi.se/data)) from `MetObs` do

```python
from smhi.metobs import MetObs
client = MetObs()
header, data = client.get_data_stationset(
    1, 192840, "corrected-archive"
)
```

Headers and data are never stored inside the `client` object.
Instead, they are explicitly returned.
To only fetch data, write

```python
from smhi.metobs import MetObs

client = MetObs()
_, data = client.get_data_stationset(1, 192840, "corrected-archive")
```

## Get data by inspecting the API

To inspect the API, the following methods are provided
The following example is a common pattern of usage

```python
from smhi.metobs import MetObs

client = MetObs()
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
header, data = client.get_data()
```
