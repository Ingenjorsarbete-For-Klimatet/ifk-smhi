# Example of Metfcts direct use

Direct usage of `Metfcts`. To list approved and valid times to

```python
from smhi.metfcts import Metfcts

client = Metfcts()
client.approved_time
client.valid_time
```

Notice that `approved_time` is the time when the Metfcts analysis was updated.
On the other hand, `valid_time` are valid time stamps to fetch data for,
see below.

To list available parameters, geographic area as polygon and points do

```python
from smhi.metfcts import Metfcts

client = Metfcts()
client.parameters
client.geo_polygon
client.get_geo_multipoint(2)
```

where `get_geo_multipoint` accepts a downsample argument.

To get data, two methods are available.
`get_point` accepts latitude and longitude arguments.
`get_multipoint` accepts `validtime`, `parameter`,
`leveltype`, `level`, `downsample` arguments.
See above to acquire a valid time and parameter.

```python
from smhi.metfcts import Metfcts

client = Metfcts()
data = client.get_point(58, 16)
data = client.get_multipoint(
    "2022-11-12T23:00:00Z", "t", "hl", 2, 2
)
```

Note that, the above valid time is outdated.
