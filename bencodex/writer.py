import collections.abc
from typing import BinaryIO, Generator, Union

from .types import BValue

__all__ = 'dump', 'dumps'


def dump(value: BValue, output: BinaryIO) -> None:
    for chunk in write(value):
        output.write(chunk)


def dumps(value: BValue) -> bytes:
    return b''.join(write(value))


def write(value: BValue) -> Generator[bytes, None, None]:
    if value is None:
        yield b'n'
        return
    elif isinstance(value, bool):
        yield b't' if value else b'f'
        return
    elif isinstance(value, int):
        yield b'i%de' % value
        return
    elif isinstance(value, (bytes, bytearray)):
        yield b'%d:' % len(value)
        yield value
        return
    elif isinstance(value, str):
        utf8 = value.encode('utf-8')
        yield b'u%d:' % len(utf8)
        yield utf8
        return
    elif isinstance(value, collections.abc.Sequence):
        yield b'l'
        for element in value:
            yield from write(element)
        yield b'e'
        return
    elif isinstance(value, collections.abc.Mapping):
        def is_unicode(k: Union[bytes, str]) -> bool:
            if isinstance(k, bytes):
                return False
            elif isinstance(k, str):
                return True
            raise TypeError('dictionary key must be a bytes or str')
        items = [
            (u, k.encode('utf-8') if u and isinstance(k, str) else k, v)
            for k, v in value.items()
            for u in [is_unicode(k)]
        ]
        items.sort()
        yield b'd'
        for u, k, v in items:
            if u:
                yield b'u'
            yield from write(k)
            yield from write(v)
        yield b'e'
        return
    raise TypeError('unsupported type: ' + repr(value))
