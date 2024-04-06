"""Utility methods."""

import logging
from datetime import datetime

import arrow
import requests
from smhi.constants import STATUS_OK

logger = logging.getLogger(__name__)


def get_request(url: str) -> requests.Response:
    """Get request from url.

    Args:
        url: url to request from

    Returns:
        response

    Raises:
        requests.exceptions.HTTPError
    """
    logger.debug(f"Fetching from {url}.")

    response = requests.get(url, timeout=200)

    if response.status_code != STATUS_OK:
        raise requests.exceptions.HTTPError(f"Could request from {url}.")

    logger.debug(f"Successful request from {url}.")

    return response


def format_datetime(test_time: str | datetime) -> str:
    """Format str and datetime to accepected time formats.

    Args:
        test_time: time to format

    Returns:
        accepted timeformat in utc as string
    """
    return arrow.get(test_time).to("utc").format("YYYYMMDDTHHmmss") + "Z"
