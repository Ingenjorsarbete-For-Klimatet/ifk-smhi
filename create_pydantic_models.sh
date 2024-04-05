#!/usr/bin/env bash
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metobs.smhi.se/api.json --class-name VersionModel --output metobs_versions.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metobs.smhi.se/api/version/1.0.json --class-name ParameterModel --output metobs_parameters.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1.json --class-name StationModel --output metobs_stations.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1/station/1.json --class-name PeriodModel --output metobs_periods.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1/station/1/period/corrected-archive.json --class-name DataModel --output metobs_data.py

datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/1/parameter.json --class-name DataModel --output mesan_parameters.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/1/approvedtime.json --class-name DataModel --output mesan_approved.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/1/validtime.json --class-name DataModel --output mesan_valid.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/1/geotype/polygon.json --class-name DataModel --output mesan_polygon.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/1/geotype/multipoint.json --class-name DataModel --output mesan_multipoint.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/1/geotype/point/lon/16/lat/58/data.json --class-name DataModel --output mesan_data_point.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url "https://opendata-download-metanalys.smhi.se/api/category/mesan2g/version/1/geotype/multipoint/validtime/20240108T060000Z/parameter/t/leveltype/hl/level/2/data.json?with-geo=true" --class-name DataModel --output mesan_data_multipoint.py

datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url "https://opendata-download-metanalys.smhi.se/api/category/strang1g/version/1/geotype/point/lon/16.158/lat/58.5812/parameter/118/data.json?from=2020-02-01&to=2020-02-02" --class-name DataModel --output strang_point.py
datamodel-codegen --output-model-type pydantic_v2.BaseModel --snake-case-field --url "http://opendata-download-metanalys.smhi.se/api/category/strang1g/version/1/geotype/multipoint/validtime/201908/parameter/118/data.json?interval=monthly" --class-name DataModel --output strang_multipoint.py
