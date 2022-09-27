from typing import Mapping, Sequence, Union

__all__ = (
    "BKey",
    "BValue",
)


BKey = Union[str, bytes]
BValue = Union[BKey, int, None, Mapping[BKey, "BValue"], Sequence["BValue"]]
# Mypy currently does not support recursive types.
# https://github.com/python/mypy/issues/731
