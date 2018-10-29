Bencodex reader/writer for Python
=================================

This package implements Bencodex_ serializtion format which extends Bencoding_.

.. _Bencodex: https://gist.github.com/dahlia/6d8e95bb598f60fecaac1dc82223a7e8
.. _Bencoding: http://www.bittorrent.org/beps/bep_0003.html#bencoding


Usage
-----

This package's API follows the tradition of Python's ``pickle`` and ``json``
modules:

- ``bencodex.dump(obj: bencodex.BValue, fileobj: typing.BinaryIO) -> None``
- ``bencodex.dumps(obj: bencodex.BValue) -> None``
- ``bencodex.load(fileobj: typing.BinaryIO) -> bencodex.BValue``
- ``bencodex.loads(encoded: bytes) -> bencodex.BValue``


License
-------

Distributed under GPLv3_ or later.

.. _GPLv3: https://www.gnu.org/licenses/gpl-3.0.html
