#!/usr/bin/env bash
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metobs.smhi.se/api.json --class-name VersionModel --output src/smhi/models/metobs_versions.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metobs.smhi.se/api/version/1.0.json --class-name ParameterModel --output src/smhi/models/metobs_parameters.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1.json --class-name StationModel --output src/smhi/models/metobs_stations.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1/station/1.json --class-name PeriodModel --output src/smhi/models/metobs_periods.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1/station/1/period/corrected-archive.json --class-name DataModel --output src/smhi/models/metobs_data.py
