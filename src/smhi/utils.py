"""Utility methods."""

import logging

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
