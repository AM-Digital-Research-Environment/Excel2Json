from typing import Optional, TypedDict


class Name(TypedDict):
    label: str
    qualifier: Optional[str]


class Role(TypedDict):
    role: str
    name: Name
    affl: list[str]
