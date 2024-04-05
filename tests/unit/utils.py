"""Unit test utils."""

import json


class MockResponse:
    def __init__(self, status, header, content):
        self.status_code = status
        self.headers = header
        self.content = content


def get_response(file, encode=False):
    """Read in response.

    Args:
        file: file to load

    Returns:
        mocked response
    """
    with open(file) as f:
        mocked_response = f.read()

    headers, content = mocked_response.split("\n\n")
    status = 200
    headers = {x.split(":")[0]: x.split(":")[1] for x in headers.split("\n")[1:]}

    if encode is True:
        content = content.encode("utf-8")

    mocked_get = MockResponse(status, headers, content)

    return mocked_get


def get_data(file, load_type=None):
    """Read in expected data structure.

    Args:
        file: file to load
        model

    Returns:
        expected pydantic model
    """
    with open(file) as f:
        if load_type == "data":
            return f.read().encode("utf-8")

        return json.load(f)
