# Example of SMHI direct use

Direct usage of `SMHI`.

## Basic use

The `SMHI` client is in an experimental state and currently only deals with `Metobs`
data. It is intended as a parent class for easy traversing of SMHI observational
data from GPS or city names directly.

The most basic usage of the client is to simply ask for data for a given station
and a given parameter:

```python
from smhi.smhi import SMHI

client = SMHI()

client.parameters.data #List all available parameters
#Parameter 1 is hourly air temperature

stations = client.get_stations(1)
stations.data #List all available stations for parameter 1

data = client.get_data(1, 72630) #Get data from specific station
#Station 72630 is Gothenburg
```

The `data` variable holds four dataframes when a single station
is used to fetch data as above.
They are called `station`, `parameter`, `period` and `df`, where the latter holds
the actual observational data. See further
[example of Metobs use](/ifk-smhi/metobs-example/).

## Interpolation

When there are several stations close to a measurement location and historical data
records are incomplete, it is convenient to use nearby stations to fill in the missing
data: This naive interpolation feature is included in the package by the parameter
`radius`. Thus, if we want to fetch historical data on the snow coverage in Kiruna,
the call is:

```python
from smhi.smhi import SMHI

client = SMHI()

#Parameter 8 is depth of snow coverage
data = client.get_data(8, 180960, 40) #Get data from specific station
#Station 180960 is Kiruna. 40 indicates we will use stations within
#a 40km radius to complement any data losses.

data2 = client.get_data(8, 180960) #Get comparison data without the
#interpolation.
```

Visualise the data:

<details>
    <summary>Scatter plot code</summary>

```python
import plotly.graph_objects as go

d1 = data.df
d2 = data2.df

index = d1.index.intersection(d2.index)
d2_dropped = d2.drop(index, axis=0)

fig = go.Figure()
fig.add_trace(
    go.Scattergl(
        x=d1.index,
        y=d1["Snödjup"],
        mode="markers",
        name="Kiruna station"
    )
)
fig.add_trace(
    go.Scattergl(
        x=d2_dropped.index,
        y=d2_dropped["Snödjup"],
        mode="markers",
        name="Interpolerat, radie 40 km"
    )
)
fig.update_layout(
    title='Historiskt snödjup i Kiruna',
    xaxis_title="År",
    yaxis_title="Snödjup [m]",
    legend={"orientation": "h"},
    margin={"l": 0, "r": 0, "b": 80, "t": 100}
)

fig.show()
```

</details>

<iframe id="igraph"
alt="Historiskt snödjup i Kiruna."
scrolling="no" style="border:none;" seamless="seamless"
src="/ifk-smhi/assets/kiruna_snodjup.html" height="525" width="100%">
</iframe>

## Finding data from a city

There are a lot of stations available: Frequently, we are simply interested
in meterological observations from a specific city. Using the library `geopy`,
this is included in the package too:

```python
from smhi.smhi import SMHI

client = SMHI()

#Parameter 8 is depth of snow coverage
data = client.get_data_by_city(8, "Kiruna", 40) #Get data from a station
#close to the city centre of Kiruna, and fill any empty holes with data
#from stations within a 40km perimeter

```
