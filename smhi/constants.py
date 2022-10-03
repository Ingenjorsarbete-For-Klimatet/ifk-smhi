"""
Constans.
"""
from collections import defaultdict

MESAN_URL = "https://opendata-download-metanalys.smhi.se"
METOBS_URL = "https://opendata-download-metobs.smhi.se/api.json"
TYPE_MAP = defaultdict(lambda: "application/json", json="application/json")
