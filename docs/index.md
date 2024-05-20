# Welcome to ifk-smhi

ifk-smhi is a python client for several SMHI APIs.
See [https://opendata.smhi.se/apidocs/](https://opendata.smhi.se/apidocs/)
for a complete list of available APIs.
SMHI stands for [Swedish Meteorological and Hydrological Institute](https://www.smhi.se/)
(or in Swedish: Sveriges meteorologiska och hydrologiska institut),
which is a Swedish agency under its parent department: Ministry of Climate and
Enterprise.

Currently, only these four APIs are supported

- Metobs - Meteorological Observations
- Metfcts - Meteorological Forecasts
- Mesan - Meteorological Analysis MESAN
- Strang - Meteorological Analysis STRÅNG (sunshine)

## Examples

Examples of direct usage of the different clients, and the experimental parent class,
are available here:

- [example of Metobs use](/ifk-smhi/metobs-example/)
- [example of Mesan use](/ifk-smhi/mesan-example/)
- [example of Metfcts use](/ifk-smhi/metfcts-example/)
- [example of Strang use](/ifk-smhi/strang-example/)
- [example of SMHI use](/ifk-smhi/smhi-example/)

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
See [example of SMHI use](/ifk-smhi/smhi-example/)
for details on how to use the client.

## Metobs client

Client to fetch data from meteorological observations.
Use this to access data from _observations_,
i.e. recorded data from weather stations scattered over north Europe.
See [example of Metobs use](/ifk-smhi/metobs-example/)
for details on how to use the client.

## Metfcts client

Client to fetch data from meteorological forecasts.
Use this to access data about _forecasts_, i.e. SMHI weather predictions.
See [example of Metfcts use](/ifk-smhi/metfcts-example/)
for details on how to use the client.

## Mesan client

Client to fetch data from meteorological analysis.
Use this to access the last 24 hour predictions of weather parameters.
This API is a useful complement to Metobs because the number of weather
stations are limited.
See [example of Mesan use](/ifk-smhi/mesan-example/)
for details on how to use the client.

## Strang client

Client to fetch data from meteorological analysis of sunshine.
Use this to access data about _sunshine_,
i.e. SMHI prediction of sunshine for a given coordinate.
This API is also a useful complement to Metobs because the number of weather
stations measureing sunshine are very limited.
See [example of Strang use](/ifk-smhi/strang-example/)
for details on how to use the client.
