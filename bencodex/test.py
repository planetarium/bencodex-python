import functools
import io
import re
from typing import Generator, Tuple
import unittest

from pkg_resources import resource_exists, resource_listdir, resource_string
from yaml import Loader, load as load_yaml

from . import dump, dumps, load, loads
from .reader import parse, parse_bytes, parse_digits, parse_text
from .writer import write

__all__ = (
    'DumpFunctions',
    'LoadFunctions',
    'ReaderFunctions',
    'WriterFunctions',
    'load_testsuite_data',
)


def load_testsuite_data() -> Generator[Tuple[str, object, bytes], None, None]:
    pkg = 'bencodex'
    suffix_re = re.compile(r'\.ya?ml$')
    for filename in resource_listdir(pkg, 'spec/testsuite'):
        if not filename.lower().endswith(('.yaml', '.yml')):
            continue
        yaml_filename = 'spec/testsuite/' + filename
        data_filename = suffix_re.sub('.dat', yaml_filename)
        if not resource_exists(pkg, data_filename):
            continue
        yaml = load_yaml(
            resource_string(pkg, yaml_filename).decode('utf-8'),
            Loader=Loader
        )
        data = resource_string(pkg, data_filename)
        yield filename, yaml, data


class DumpFunctions(unittest.TestCase):

    def test_dump(self):
        for filename, yaml, data in load_testsuite_data():
            with self.subTest(filename=filename), io.BytesIO() as f:
                dump(yaml, f)
                self.assertEqual(data, f.getvalue())

    def test_dumps(self):
        for filename, yaml, data in load_testsuite_data():
            with self.subTest(filename=filename):
                self.assertEqual(data, dumps(yaml))


class LoadFunctions(unittest.TestCase):

    def test_loads(self):
        for filename, yaml, data in load_testsuite_data():
            with self.subTest(filename=filename):
                self.assertEqual(yaml, loads(data))

    def test_load(self):
        for filename, yaml, data in load_testsuite_data():
            with self.subTest(filename=filename), io.BytesIO(data) as f:
                self.assertEqual(yaml, load(f))


class ReaderFunctions(unittest.TestCase):

    def test_parse_null(self):
        input = io.BytesIO(b'n')
        buffer = bytearray()
        self.assertIsNone(parse(buffer, input))
        self.assertFalse(buffer)
        self.assertFalse(input.read())

        input = io.BytesIO()
        buffer = bytearray(b'ni123e')
        self.assertIsNone(parse(buffer, input))
        self.assertEqual(b'i123e', buffer + input.read())

    def test_parse_bool(self):
        input = io.BytesIO(b't')
        buffer = bytearray()
        self.assertIs(True, parse(buffer, input))
        self.assertFalse(buffer)
        self.assertFalse(input.read())

        input = io.BytesIO()
        buffer = bytearray(b'ft')
        self.assertIs(False, parse(buffer, input))
        self.assertEqual(b't', buffer + input.read())

    def test_parse_int(self):
        input = io.BytesIO(b'i123e')
        buffer = bytearray()
        self.assertEqual(123, parse(buffer, input))
        self.assertFalse(buffer)
        self.assertFalse(input.read())

        input = io.BytesIO(b'34en')
        buffer = bytearray(b'i12')
        self.assertEqual(1234, parse(buffer, input))
        self.assertEqual(b'n', buffer + input.read())

        input = io.BytesIO(b'i-456e')
        buffer = bytearray()
        self.assertEqual(-456, parse(buffer, input))
        self.assertFalse(buffer)
        self.assertFalse(input.read())

        input = io.BytesIO(b'i0e')
        buffer = bytearray()
        self.assertEqual(0, parse(buffer, input))
        self.assertFalse(buffer)
        self.assertFalse(input.read())

    def test_parse_list(self):
        enc = b'li123eltnfed3:keyu5:value1:znetfnldu1:k1:vei123eee'
        val = [
            123,
            [True, None, False],
            {b'key': 'value', b'z': None},
            True, False, None,
            [{'k': b'v'}, 123]
        ]

        for buffer_size in range(len(enc) + 1):
            with self.subTest(buffer_size=buffer_size):
                input = io.BytesIO(enc[buffer_size:])
                buffer = bytearray(enc[:buffer_size])
                self.assertEqual(val, parse(buffer, input))
                self.assertFalse(buffer)
                self.assertFalse(input.read())

                input = io.BytesIO(enc[buffer_size:] + b'n')
                buffer = bytearray(enc[:buffer_size])
                self.assertEqual(val, parse(buffer, input))
                self.assertEqual(b'n', buffer + input.read())

    def test_parse_dict(self):
        input = io.BytesIO(b'de')
        buffer = bytearray()
        self.assertEqual({}, parse(buffer, input))
        self.assertFalse(buffer)
        self.assertFalse(input.read())

        enc = b'd1:ku1:v2:k3du1:k1:veu2:k2ltfee'
        val = {b'k': 'v', 'k2': [True, False], b'k3': {'k': b'v'}}

        for buffer_size in range(len(enc) + 1):
            with self.subTest(buffer_size=buffer_size):
                input = io.BytesIO(enc[buffer_size:])
                buffer = bytearray(enc[:buffer_size])
                self.assertEqual(val, parse(buffer, input))
                self.assertFalse(buffer)
                self.assertFalse(input.read())

                input = io.BytesIO(enc[buffer_size:] + b'n')
                buffer = bytearray(enc[:buffer_size])
                self.assertEqual(val, parse(buffer, input))
                self.assertEqual(b'n', buffer + input.read())

        with self.assertRaises(
                ValueError,
                msg='key must be a Unicode/byte string'):
            parse(bytearray(), io.BytesIO(b'du1:ku1:v2:k2u2:v2i3eu2:v3e'))

    def test_parse_text(self):
        u = b'\xec\x9c\xa0\xeb\x8b\x88\xec\xbd\x94\xeb\x93\x9c'
        t = '\uc720\ub2c8\ucf54\ub4dc'
        for prefix, p in (b'', parse_text), (b'u', parse):
            with self.subTest(p.__qualname__):
                input = io.BytesIO(prefix + b'12:' + u + b'n')
                buffer = bytearray()
                self.assertEqual(t, p(buffer, input))
                self.assertEqual(b'n', buffer + input.read())

                input = io.BytesIO(u[5:] + b'f')
                buffer = bytearray(prefix + b'12:' + u[:5])
                self.assertEqual(t, p(buffer, input))
                self.assertEqual(b'f', buffer + input.read())

    def test_parse_bytes(self):
        for msg, p in [('parse_bytes', functools.partial(parse_bytes, b'')),
                       ('parse', parse)]:
            with self.subTest(msg):
                input = io.BytesIO(b'11:hello worldn')
                buffer = bytearray()
                self.assertEqual(b'hello world', p(buffer, input))
                self.assertEqual(b'n', buffer + input.read())

                input = io.BytesIO(b'lo worldf')
                buffer = bytearray(b'11:hel')
                self.assertEqual(b'hello world', p(buffer, input))
                self.assertEqual(b'f', buffer + input.read())

        input = io.BytesIO(b'1:hello worldt')
        buffer = bytearray()
        self.assertEqual(b'hello world', parse_bytes(b'1', buffer, input))
        self.assertEqual(b't', buffer + input.read())

        input = io.BytesIO(b'lo world')
        buffer = bytearray(b'1:hel')
        self.assertEqual(b'hello world', parse_bytes(b'1', buffer, input))
        self.assertFalse(buffer + input.read())

    def test_parse_digits(self):
        input = io.BytesIO(b'123e')
        buffer = bytearray()
        self.assertEqual(123, parse_digits(b'e', buffer, input))
        self.assertFalse(buffer)
        self.assertFalse(input.read())

        input = io.BytesIO(b'456e')
        buffer = bytearray(b'123')
        self.assertEqual(123456, parse_digits(b'e', buffer, input))
        self.assertFalse(buffer)
        self.assertFalse(input.read())

        input = io.BytesIO(b'123et')
        buffer = bytearray()
        self.assertEqual(123, parse_digits(b'e', buffer, input))
        self.assertEqual(b't', buffer + input.read())

        input = io.BytesIO(b'e')
        buffer = bytearray()
        with self.assertRaises(ValueError) as cm:
            parse_digits(b'e', buffer, input)
        self.assertEqual("expected 10-base digits: b''", str(cm.exception))

        input = io.BytesIO(b'123')
        buffer = bytearray()
        with self.assertRaises(ValueError) as cm:
            parse_digits(b'e', buffer, input)
        self.assertEqual("expected a byte b'e' (0x65)", str(cm.exception))

        input = io.BytesIO(b'7be')
        buffer = bytearray()
        with self.assertRaises(ValueError) as cm:
            parse_digits(b'e', buffer, input)
        self.assertEqual("expected 10-base digits: b'7b'", str(cm.exception))


class WriterFunctions(unittest.TestCase):

    def test_write_null(self):
        self.assertEqual(b'n', b''.join(write(None)))

    def test_write_bool(self):
        self.assertEqual(b't', b''.join(write(True)))
        self.assertEqual(b'f', b''.join(write(False)))

    def test_write_int(self):
        self.assertEqual(b'i123e', b''.join(write(123)))
        self.assertEqual(b'i-456e', b''.join(write(-456)))
        self.assertEqual(b'i0e', b''.join(write(0)))

    def test_write_bytes(self):
        self.assertEqual(b'11:hello world', b''.join(write(b'hello world')))

    def test_write_unicode(self):
        self.assertEqual(
            b'u12:\xec\x9c\xa0\xeb\x8b\x88\xec\xbd\x94\xeb\x93\x9c',
            b''.join(write('\uc720\ub2c8\ucf54\ub4dc'))
        )

    def test_write_list(self):
        val = [
            123,
            [True, None, False],
            {b'key': 'value', b'z': None},
            True, False, None,
            [{'k': b'v'}, 123]
        ]
        enc = b'li123eltnfed3:keyu5:value1:znetfnldu1:k1:vei123eee'
        self.assertEqual(enc, b''.join(write(val)))

    def test_write_dict(self):
        self.assertEqual(b'de', b''.join(write({})))
        val = {b'k': 'v', 'k2': [True, False], b'k3': {'k': b'v'}}
        enc = b'd1:ku1:v2:k3du1:k1:veu2:k2ltfee'
        self.assertEqual(enc, b''.join(write(val)))
