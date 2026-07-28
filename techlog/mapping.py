# techlog/mapping.py

import typing
from dataclasses import fields, is_dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum


def _unwrap_optional(tp):
    if typing.get_origin(tp) is typing.Union:
        args = [a for a in typing.get_args(tp) if a is not type(None)]
        if len(args) == 1:
            return args[0]
    return tp


def from_api(dataclass_type, data):
    if data is None:
        return None

    kwargs = {}

    for f in fields(dataclass_type):
        if f.name not in data:
            continue

        value = data[f.name]

        if value is None:
            kwargs[f.name] = None
            continue

        field_type = _unwrap_optional(f.type)

        if is_dataclass(field_type):
            kwargs[f.name] = from_api(field_type, value)
        elif isinstance(field_type, type) and issubclass(field_type, Enum):
            kwargs[f.name] = field_type(value)
        elif field_type is datetime:
            kwargs[f.name] = datetime.fromisoformat(value.replace("Z", "+00:00"))
        elif field_type is date:
            kwargs[f.name] = date.fromisoformat(value)
        elif field_type is time:
            kwargs[f.name] = time.fromisoformat(value)
        elif field_type is Decimal:
            kwargs[f.name] = Decimal(str(value))
        else:
            kwargs[f.name] = value

    return dataclass_type(**kwargs)

def from_api_many(dataclass_type, data):
    """
    Build a list of dataclass_type instances from a list of dicts,
    or from a paginated response like {"results": [...]}.
    """

    if isinstance(data, dict) and "results" in data:
        data = data["results"]

    return [from_api(dataclass_type, item) for item in data]