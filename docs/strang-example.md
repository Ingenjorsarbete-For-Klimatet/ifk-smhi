# Example of Strang direct use

Direct usage of `Strang`.

## Parameters

All available parameters can be listed as

```python
from smhi.strang import Strang

client = Strang()
response = client.parameters
```

## Point and multipoint data

To get a point response from `Strang` do

```python
from smhi.strang import Strang

client = Strang()
response = client.get_point(
    58, 16, 118, "2020-01-01", "2020-02-01", "hourly"
)
```

and for a multi point response

```python
from smhi.strang import Strang

client = Strang()
response = client.get_multipoint(116, "2022-01-01", "monthly")
```

The return objects are of type `StrangPointModel` and `StrangMultiPointModel`,
respectively. This will show the data in a dataframe

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
