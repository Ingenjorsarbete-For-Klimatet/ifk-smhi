# Example of Strang direct use

Direct usage of `Strang`. To get a point response from `Strang` do

```python
from smhi.strang import Strang

client = Strang()
data = client.get_point(
    58, 16, 118, "2020-01-01", "2020-02-01", "hourly"
)
```

and for a multi point response

```python
from smhi.strang import Strang

client = Strang()
data = client.get_multipoint(
    116, "2022-01-01", "monthly"
)
```

Data is not stored inside the class, but get status and headers are.
They can be accessed as

```python
from smhi.strang import Strang

client = Strang()
data = client.get_multipoint(116, "2022-01-01", "monthly")
client.status
client.header
```
