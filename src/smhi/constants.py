"""
Constans.
"""
from collections import defaultdict


METOBS_URL = "https://opendata-download-metobs.smhi.se/api.json"
TYPE_MAP = defaultdict(lambda: "application/json", json="application/json")
