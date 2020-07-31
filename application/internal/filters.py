"""Jinja Filters."""
from typing import Union

def usd(value: Union[int, float]) -> str:
    return f"${value:,.2f}"

def capitalize(name: str) -> str:
    return name.capitalize()
