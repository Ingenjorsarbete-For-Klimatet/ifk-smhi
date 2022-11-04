
Direct usage of `MetObs`, without using the `SMHI` client is possible.
To get data from a known station (found e.g. through exploration of https://www.smhi.se/data) from `MetObs` do

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

