Bencodex reader/writer for Python
=================================

.. image:: https://travis-ci.com/planetarium/bencodex-python.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.com/planetarium/bencodex-python

This package implements Bencodex_ serialization format which extends Bencoding_.

.. _Bencodex: https://github.com/planetarium/bencodex
.. _Bencoding: http://www.bittorrent.org/beps/bep_0003.html#bencoding


Usage
-----

This package's API follows the tradition of Python's ``pickle`` and ``json``
modules:

- ``bencodex.dump(obj: bencodex.BValue, fileobj: typing.BinaryIO) -> None``
- ``bencodex.dumps(obj: bencodex.BValue) -> bytes``
- ``bencodex.load(fileobj: typing.BinaryIO) -> bencodex.BValue``
- ``bencodex.loads(encoded: bytes) -> bencodex.BValue``


Examples
--------

>>> from bencodex import dumps, loads
>>> dumps({'name': 'Jane Doe', 'age': 30, 'nationality': ['BR', 'US']})
b'du3:agei30eu4:nameu8:Jane Doeu11:nationalitylu2:BRu2:USee'
>>> loads(_)
{'age': 30, 'name': 'Jane Doe', 'nationality': ['BR', 'US']}


License
-------

Distributed under GPLv3_ or later.

.. _GPLv3: https://www.gnu.org/licenses/gpl-3.0.html
