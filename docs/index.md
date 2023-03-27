# Welcome to ifk-smhi

ifk-smhi is a python client for several SMHI APIs.
See [https://opendata.smhi.se/apidocs/](https://opendata.smhi.se/apidocs/)
for a complete list of available APIs.
SMHI stands for [Swedish Meteorological and Hydrological Institute](https://www.smhi.se/)
(or in Swedish: Sveriges meteorologiska och hydrologiska institut),
which is a Swedish agency under its parent department:  Ministry of Climate and
Enterprise.

Initially only these four APIs are supported

- Metobs - Meteorological Observations
- Metfcts - Meteorological Forecasts
- Mesan - Meteorological Analysis MESAN
- Strang - Meteorological Analysis STRÅNG (sunshine)

## Install

ifk-smhi can be installed as

```bash
pip install ifk-smhi
```

For the latest build, install from GitHub

```bash
pip install git+https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi.git@main
```

## SMHI client

The SMHI client is in an experimental state.
As of now, it only controls the Metobs sub-client.
It will be expanded in future versions.

## Metobs client

Client to fetch data from meteorological observations.
Use this to access data from _observations_,
i.e. recorded data from weather stations scattered over north Europe.

## Metfcts client

Client to fetch data from meteorological forecasts.
Use this to access data about _forecasts_, i.e. SMHI weather predictions.

## Mesan client

Client to fetch data from meteorological analysis.
Use this to access up to 24 hour predictions of weather parameters.
This API is a useful complement to Metobs because the number of weather
stations are limited.

## Strang client

Client to fetch data from meteorological analysis of sunshine.
Use this to access data about _sunshine_,
i.e. SMHI prediction of sunshine for a given coordinate.
