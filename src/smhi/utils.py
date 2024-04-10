"""Utility methods."""

import logging
from datetime import datetime
from typing import Union

import arrow
import requests
from smhi.constants import OUT_OF_BOUNDS, STATUS_OK

logger = logging.getLogger(__name__)


def get_request(url: str) -> requests.Response:
    """Get request from url.

    Args:
        url: url to request from

    Returns:
        response

    Raises:
        ValueError
        requests.exceptions.HTTPError
    """
    logger.debug(f"Fetching from {url}.")

    response = requests.get(url, timeout=200)

    if response.status_code != STATUS_OK:
        if OUT_OF_BOUNDS in response.text.lower():
            raise ValueError("Request is out of bounds.")

        raise requests.exceptions.HTTPError(f"Could not request from {url}.")

    logger.debug(f"Successful request from {url}.")

    return response


def format_datetime(test_time: Union[str, datetime]) -> str:
    """Format str and datetime to accepected time formats.

    Args:
        test_time: time to format

    Returns:
        accepted timeformat in utc as string
    """
    return arrow.get(test_time).to("utc").format("YYYYMMDDTHHmmss") + "Z"
