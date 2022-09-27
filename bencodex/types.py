from typing import Mapping, Sequence, Union

__all__ = (
    "BKey",
    "BValue",
)


BKey = Union[str, bytes]
BValue = Union[BKey, int, None, Mapping[BKey, "BValue"], Sequence["BValue"]]
# Mypy currently supports recursive types as experimental feature.
# You have to run mypy with '--enable-recursive-aliases' otpion.
# https://github.com/python/mypy/issues/731
# https://github.com/python/mypy/pull/13297
