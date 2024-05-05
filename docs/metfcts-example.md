# Example of Metfcts direct use

Direct usage of `Metfcts`. Note that `Mesan` and `Metfcts` have identical interfaces.

## Time listing

To list approved and valid times to

```python
from smhi.metfcts import Metfcts

client = Metfcts()
client.approved_time
# approved time object

client.valid_time
# valid time object

vt = client.valid_time
vt.valid_time
# returns a list of valid datetimes
```

Notice that `approved_time` is the time when the Metfcts analysis was updated.
On the other hand, `valid_time` are valid time stamps to fetch data for,
see below.

## Parameters and geographic area

To list available parameters, geographic area as polygon and points do

```python
from smhi.metfcts import Metfcts

client = Metfcts()

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
`get_multipoint` accepts `validtime`, `parameter`,
`leveltype`, `level`, `geo` and `downsample` arguments.
See above to acquire a valid time and parameter.

Note that the date input can be in either `str` or `datetime` formats.
The API expects times in UTC but the client expects the user to input
local datetimes. The local datetimes are converted to UTC before an API request
is performed.

```python
from smhi.metfcts import Metfcts

client = Metfcts()

point = client.get_point(58, 16)
point.df
# dataframe of actual data

point.df_info
# dataframe with information about available parameters

multipoint = client.get_multipoint(
    "2024-04-1206T16:00:00Z", "t", "hl", 2, 2
)
```

Note that, the above valid time is outdated.
