# Example of Mesan direct use

Direct usage of `Mesan`.

## Time listing

To list approved and valid times to

```python
from smhi.mesan import Mesan

client = Mesan()
client.created_time
# approved time object

client.times
# valid time object

vt = client.times
vt.times
# returns a list of valid datetimes
```

Notice that `created_time` is the time when the MESAN analysis was updated.
On the other hand, `times` are valid time stamps to fetch data for,
see below.

## Parameters and geographic area

To list available parameters, geographic area as polygon and points do

```python
from smhi.mesan import Mesan

client = Mesan()

parameters = client.parameters
parameters.parameter
# list of all parameter codes and their meaning

client.parameter_descriptions
# mapping of parameter codes from above and a more descriptive meaning

client.parameter_descriptions[parameters.parameter[0].name]
# descriptive meaning of parameter

geopoly = client.geo_polygon
geopoly.coordinates
# polygon of geographic area as a list

geomultipoint = client.get_geo_multipoint(2)
# all coordinates of value points as a list
```

where `get_geo_multipoint` accepts a downsample argument.

## Point and multipoint data

To get data, two methods are available.
`get_point` accepts latitude and longitude arguments.
`get_multipoint` accepts `times`, `parameter`,
`geo` and `downsample` arguments.
See above to acquire a valid time and parameter.

Note that the date input can be in either `str` or `datetime` formats.
The API expects times in UTC but the client expects the user to input
local datetimes. The local datetimes are converted to UTC before an API request
is performed.

```python
from smhi.mesan import Mesan

client = Mesan()

point = client.get_point(58, 16)
point.df
# dataframe of actual data

multipoint = client.get_multipoint(
    client.times.times[-1], "air_temperature", True, 2
)
```
