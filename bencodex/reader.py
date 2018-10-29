import io
from typing import BinaryIO, Union

from .types import BValue

__all__ = 'load', 'loads'


def load(input: BinaryIO) -> BValue:
    buffer = bytearray()
    v = parse(buffer, input)
    if not buffer:
        buffer += input.read(1)
    offset = input.tell()
    if buffer:
        raise ValueError(
            'unexpected byte at {0}: {1!r} (0x{2:02x})'.format(
                offset - len(buffer),
                buffer[:1],
                buffer[0],
            )
        )
    return v


def loads(bencoding: Union[bytes, bytearray]) -> BValue:
    with io.BytesIO(bencoding) as f:
        return load(f)


def parse(buffer: bytearray, input: BinaryIO) -> BValue:
    if buffer:
        prefix = bytes([buffer.pop(0)])
    else:
        prefix = input.read(1)
    if prefix == b'n':
        return None
    elif prefix == b't':
        return True
    elif prefix == b'f':
        return False
    elif prefix == b'i':
        if not buffer:
            buffer += input.read(1)
        if buffer[:1] == b'-':
            buffer.pop(0)
            sign = -1
        else:
            sign = +1
        return sign * parse_digits(b'e', buffer, input)
    elif prefix == b'u':
        return parse_text(buffer, input)
    elif prefix == b'l':
        elements = []
        while True:
            if not buffer:
                buffer += input.read(8)
            if buffer[:1] == b'e':
                buffer.pop(0)
                break
            element = parse(buffer, input)
            elements.append(element)
        return elements
    elif prefix == b'd':
        pairs = []
        while True:
            if not buffer:
                buffer += input.read(8)
            if buffer[:1] == b'e':
                buffer.pop(0)
                break
            if buffer[:1] == b'u':
                buffer.pop(0)
                key = parse_text(buffer, input)  # type: Union[str, bytes]
            elif buffer[:1].isdigit():
                key = parse_bytes(b'', buffer, input)
            else:
                raise ValueError('key must be a Unicode/byte string')
            value = parse(buffer, input)
            pairs.append((key, value))
        return dict(pairs)
    elif prefix.isdigit():
        return parse_bytes(prefix, buffer, input)
    raise ValueError(
        'unexpected byte at {0}: {1!r} (0x{2:02x})'.format(
            input.tell() - len(buffer) - 1,
            prefix,
            prefix[0],
        )
    )


def parse_text(buffer: bytearray, input: BinaryIO) -> str:
    return parse_bytes(b'', buffer, input).decode('utf-8')


def parse_bytes(prefix: bytes, buffer: bytearray, input: BinaryIO) -> bytes:
    if prefix:
        buffer[:0] = prefix
    size = parse_digits(b':', buffer, input)
    if len(buffer) < size:
        buffer += input.read(size - len(buffer))
    content = bytes(buffer[:size])
    del buffer[:size]
    return content


def parse_digits(terminator: bytes, buffer: bytearray, input: BinaryIO) -> int:
    if not buffer:
        buffer += input.read(len(terminator))
    while True:
        try:
            pos = buffer.index(terminator)
        except ValueError:
            chunk = input.read(8)
            if not chunk:
                raise ValueError(
                    'expected a byte {0!r} (0x{1:02x})'.format(
                        terminator,
                        terminator[0],
                    )
                )
            buffer += chunk
        else:
            if buffer[:pos].isdigit():
                v = int(buffer[:pos])
                del buffer[:pos + len(terminator)]
                return v
            raise ValueError(
                'expected 10-base digits: ' +
                repr(bytes(buffer[:pos]))
            )
