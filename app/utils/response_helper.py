# app/utils/response_helper.py
from typing import Any


def create_response(status: str, msg: str, data: Any = None):
    """
    Create a uniform response structure.
    """
    return {
        "status": status,
        "msg": msg,
        "data": data,
    }
