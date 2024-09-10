from collections.abc import Iterable
from typing import TypedDict


class Name(TypedDict):
    label: str
    qualifier: str | None


class Role(TypedDict):
    role: str
    name: Name
    affl: Iterable[str]
