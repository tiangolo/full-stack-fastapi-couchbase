from enum import Enum
from typing import Callable, Dict, Set
from types import GeneratorType

from pydantic import BaseModel
from pydantic.json import ENCODERS_BY_TYPE

ENCODERS: Dict[type, Callable] = {}

ENCODERS.update(ENCODERS_BY_TYPE)
ENCODERS.update({str: str, int: int, float: float, bool: bool, type(None): lambda n: n})
SEQUENCES = [list, set, frozenset, GeneratorType, tuple]


def json_dict_encoder(obj):
    if isinstance(obj, CustomBaseModel):
        return obj.json_dict()
    if isinstance(obj, Enum):
        return json_dict_encoder(obj.value)
    if isinstance(obj, dict):
        encoded_dict = {}
        for key in obj:
            encoded_dict[key] = json_dict_encoder(obj[key])
        return encoded_dict
    for sequence in SEQUENCES:
        if isinstance(obj, sequence):
            return [json_dict_encoder(item) for item in obj]
    try:
        encoder = ENCODERS[type(obj)]
    except KeyError:
        raise TypeError(
            f"Object of type '{obj.__class__.__name__}' is not JSON serializable"
        )
    else:
        return encoder(obj)


class CustomBaseModel(BaseModel):
    class Config:
        use_enum_values = True

    def json_dict(
        self,
        *,
        include: Set[str] = None,
        exclude: Set[str] = set(),
        by_alias: bool = False,
    ):
        model_dict = self.dict(include=include, exclude=exclude, by_alias=by_alias)
        return json_dict_encoder(model_dict)
