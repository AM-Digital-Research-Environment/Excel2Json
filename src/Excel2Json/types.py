from typing import Optional, TypedDict

class Name(TypedDict):
    label: Optional[str]
    qualifier: Optional[str]

class Role(TypedDict):
    name: Name
    affl: Optional[list[str]]
