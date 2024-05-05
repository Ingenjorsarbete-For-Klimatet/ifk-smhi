# Example of Strang direct use

Direct usage of `Strang`.

## Parameters

All available parameters can be listed as

```python
from smhi.strang import Strang

client = Strang()
parameters = client.parameters
# prints parameters and also returns a list with parameter numbers
```

## Point data

To get a point response from `Strang` do

```python
from smhi.strang import Strang

client = Strang()
point = client.get_point(
    latitude=58,
    longitude=16,
    parameter=118,
    time_from="2020-01-01",
    time_to="2020-02-01",
    time_interval="hourly",
)
```

Note that the date input can be in either `str` or `datetime` formats.
The API expects times in UTC but the client expects the user to input
local datetimes. The local datetimes are converted to UTC before an API request
is performed.

That is, this will work fine

```python
from datetime import datetime
from smhi.strang import Strang

client = Strang()
point = client.get_point(
    58,
    16,
    118,
    "2020 01 01",
    datetime.strptime("2020-02-01", '%Y-%m-%d').date(),
    "hourly",
)
```

The return object is of type `StrangPoint`. For a full list of available
fields see [strang model](/ifk-smhi/strang-model/).

```python
response.df
```

while shows what the selected parameter means.

```python
response.parameter_meaning
```

## Multipoint data

For a multi point response

```python
from smhi.strang import Strang

client = Strang()
response = client.get_multipoint(116, "2022-01-01", "monthly")
```

Also here, the datetime input can be in either `str` or `datetime` formats.

The return objects is of type `StrangMultiPoint`.
For a full list of available fields see
[strang model](/ifk-smhi/strang-model/).

This will show the data in a dataframe

```python
response.df
```

while shows what the selected parameter means.

```python
response.parameter_meaning
```

The URL used to fetch from is stored in

```python
response.url
```
