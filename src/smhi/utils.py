"""Utility methods."""

import logging

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
        logger.warning(f"Request failed for {url}.")
    else:
        logger.debug(f"Successful request from {url}.")

    return response
