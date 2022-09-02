import argparse
import io
import pprint
import re
import shutil
import sys
from typing import Optional

from bencodex import load

__all__ = 'main',

parser = argparse.ArgumentParser(
    description='Debug-friendly Bencodex formatter',
)
parser.add_argument(
    'file',
    metavar='FILE',
    nargs='?',
    help='the path of the Bencodex file to show.  if omitted (default) it '
         'expects the Bencodex data from the standard input'
)
parser.add_argument(
    '-x', '--hex-input',
    action='store_true',
    default=False,
    help='expects the input data is not binary, but hexadecimal text'
)


def read_input(path: Optional[str], hex: bool):
    if path is None:
        # Pipes are not seekable
        if hex:
            data = hex_to_bin(sys.stdin.read())
        else:
            data = sys.stdin.buffer.read()
        return io.BytesIO(data)
    elif hex:
        with open(path, 'r') as f:
            hex_data = f.read()
        data = hex_to_bin(hex_data)
        return io.BytesIO(data)
    return open(path, 'rb')


def hex_to_bin(hex: str) -> bytes:
    return bytes.fromhex(re.sub(r'[\s.,:;_-]+', '', hex))


def main() -> None:
    args = parser.parse_args()
    term_size = shutil.get_terminal_size()
    with read_input(args.file, args.hex_input) as f:
        tree = load(f)
    try:
        pprint.pprint(tree, width=term_size.columns, compact=True)
    except KeyboardInterrupt:
        raise SystemExit(130)


if __name__ == '__main__':
    main()
