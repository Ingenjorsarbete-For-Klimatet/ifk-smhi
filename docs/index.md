# Welcome to ifk-smhi

ifk-smhi is a python client for several SMHI APIs.
See [https://opendata.smhi.se/apidocs/](https://opendata.smhi.se/apidocs/)
for a complete list of available APIs.
SMHI stands for [Swedish Meteorological and Hydrological Institute](https://www.smhi.se/)
(or in Swedish: Sveriges meteorologiska och hydrologiska institut),
which is a Swedish agency under its parent department: Ministry of the Environment.

Initially only these four APIs are supported:

- Metobs - Meteorological Observations
- Metfcts - Meteorological Forecasts
- Mesan - Meteorological Analysis MESAN
- Strang - Meteorological Analysis STRÅNG (sunshine)

## Install

This package is not yet registered with pypi. For now, install from github

```bash
pip install git+https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi.git@main
```

## SMHI client

The SMHI client can be used as a single object coordinating sub-clients,
e.g. Metobs or Strang.

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
