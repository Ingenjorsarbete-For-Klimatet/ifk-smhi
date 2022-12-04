# Example of Strang direct use

Direct usage of `Strang`, without using the `SMHI` client is possible.
To get a point response from `Strang` do

```python
from smhi.strang import Strang

client = Strang()
data, headers, status= client.get_point(
    58, 16, 118, "2020-01-01", "2020-02-01", "hourly"
)
```

and for a multi point response

```python
from smhi.strang import Strang

client = Strang()
data, headers, status= client.get_multipoint(
    116, "2022-01-01", "monthly"
)
```

Status, headers and data are never stored inside the `client` object.
Instead, they are explicitly returned.
To only fetch data, write

```python
from smhi.strang import Strang

client = Strang()
data, _, _ = client.get_multipoint(116, "2022-01-01", "monthly")
```
