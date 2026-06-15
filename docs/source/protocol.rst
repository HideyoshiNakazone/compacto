
Wire Protocol
=============

Every call to :func:`pack` produces a self-describing binary buffer. This page
documents the exact byte-level layout so you can implement a reader in any
language.

.. contents:: Contents
   :local:
   :depth: 2

----

Frame Layout
------------

A compacto frame is split into two regions: a fixed-structure **header** and a
variable-length **payload**. The header always comes first and is always encoded
in big-endian byte order, regardless of the payload byte order chosen at encode
time.

.. code-block:: text

    ┌────────────────────────────────────────────────────────────────────┐
    │                         COMPACTO FRAME                             │
    ├──────────┬──────────┬──────────────────────────┬───────────────────┤
    │ Options  │ Version  │       Schema Hash        │      Payload      │
    │ uint16   │ uint16   │    uint32 or uint64      │    (variable)     │
    │  2 bytes │  2 bytes │      4 or 8 bytes        │                   │
    ├──────────┴──────────┴──────────────────────────┴───────────────────┤
    │◄────────────── HEADER (always big-endian) ───────────────────────►│
    └────────────────────────────────────────────────────────────────────┘

Byte offsets (default 4-byte hash):

.. code-block:: text

    Offset │ Field
    ───────┼──────────────────────────────────
     0x00  │ Options  (high byte)
     0x01  │ Options  (low byte)
     0x02  │ Version  (high byte)
     0x03  │ Version  (low byte)
     0x04  │ Schema Hash  (byte 0)
     0x05  │ Schema Hash  (byte 1)
     0x06  │ Schema Hash  (byte 2)
     0x07  │ Schema Hash  (byte 3)
     0x08  │ Payload starts here …

When the ``IS_8_BYTE_HASH`` option flag is set the hash occupies bytes 4–11 and
the payload starts at byte 12.

----

Header Fields
-------------

Options (bytes 0–1)
~~~~~~~~~~~~~~~~~~~

A ``uint16`` bitmask. Individual bits are defined as:

.. list-table::
   :header-rows: 1
   :widths: 8 12 20 60

   * - Bit
     - Mask
     - Name
     - Effect
   * - 0
     - ``0x0001``
     - ``IS_LITTLE_ENDIAN``
     - Payload is encoded in little-endian byte order. The header remains
       big-endian. Pass ``is_little_endian=True`` to :func:`pack` to set this
       flag.
   * - 1
     - ``0x0002``
     - ``IS_8_BYTE_HASH``
     - The schema hash field is a ``uint64`` (8 bytes) instead of the default
       ``uint32`` (4 bytes). Pass ``is_8_byte_hash=True`` to :func:`pack` to
       set this flag. This shifts the payload start from byte 8 to byte 12.
   * - 2
     - ``0x0004``
     - ``IS_LENGTH_64_BYTES``
     - Length prefixes for ``str``, ``bytes``, ``list``, and ``dict`` fields
       are encoded as ``uint64`` (8 bytes) instead of the default ``uint32``
       (4 bytes). Pass ``is_length_64_bytes=True`` to :func:`pack` to set this
       flag.
   * - 3–15
     - —
     - *(reserved)*
     - Unknown flags should be ignored to preserve forward compatibility.

Version (bytes 2–3)
~~~~~~~~~~~~~~~~~~~

A ``uint16`` encoding the protocol version, packed as ``(major << 8) | revision``.
The current version is **1.0** — encoded as ``0x0100``.

:func:`unpack` validates this value against its own ``PROTOCOL_VERSION`` constant.
A version mismatch raises :exc:`InvalidHeaderException` immediately, before any
field is decoded.

Schema Hash (bytes 4–7 or 4–11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A `BLAKE2b <https://blake2.net/>`_ digest of the struct's *typing tree*: a
recursive description of each field name, its type-definition class, and the
underlying ``ctypes`` implementation type.

The hash is computed as follows:

1. For each node in the tree (depth-first), feed:

   * the name of the type-definition class (e.g. ``"FieldsDeff"``, ``"StringDeff"``),
   * the field name as UTF-8 bytes,
   * for primitive fields (``FieldsDeff``), the ``ctypes`` class name (e.g.
     ``"c_double"``, ``"c_int32"``).

2. Each child's digest is fed into the parent's hasher so the entire tree
   structure contributes to the final value.

The digest is **4 bytes** by default; **8 bytes** when ``IS_8_BYTE_HASH`` is set.

**What changes the hash:**

* Renaming a class or any field.
* Reordering fields (order is structural).
* Changing a field's type — including its ctypes precision (``c_int32`` →
  ``c_int64`` will produce a different hash).
* Adding or removing a field.
* Changing a field from a primitive to a nested object or vice-versa.

**What does not change the hash:**

* The actual field *values* — only the schema is hashed.
* Python-level metadata such as docstrings, default values, or validators.

:func:`unpack` computes an expected hash from the target class and compares it
to the hash embedded in the buffer. If they differ, :exc:`InvalidHeaderException`
is raised before any payload byte is touched.

----

Why the Header is Always Big-Endian
------------------------------------

The ``IS_LITTLE_ENDIAN`` flag controls *payload* byte order, but the flag itself
lives in the header. If the header were encoded in the same byte order as the
payload, a reader would need to try both byte orders to determine which one
applies — a chicken-and-egg problem.

By fixing the header to big-endian, any reader can always parse the header
unconditionally and then switch to the correct byte order for the payload.

----

Parsing Tree and Traversal Order
---------------------------------

Before the first byte is encoded or decoded, compacto calls ``struct_parser``
to build a **typing tree** from the Python class annotations.  Every encoder
and every decoder operates on this tree — it is the single authority on both
the schema hash (see `Header Fields`_) and the exact byte layout of the payload.

Node Types
~~~~~~~~~~

Each node in the tree is one of the following types.  The children of each
node are listed in the order they are stored; that order governs the sequence
in which fields appear in the payload.

.. list-table::
   :header-rows: 1
   :widths: 18 25 57

   * - Node type
     - Children (left → right)
     - Description
   * - ``ObjectDeff``
     - One child per field, **in declaration order**
     - Root node and inline-nested-struct nodes.  Children are ordered exactly
       as :func:`typing.get_type_hints` returns them — which reflects the
       top-to-bottom, left-to-right source order of the class body.
   * - ``ListDeff``
     - ``_element``
     - Single child describing the element type ``T`` in ``list[T]``.
   * - ``HashmapDeff``
     - ``_key``, ``_value``
     - Two children: child 0 is the key type ``K``, child 1 is the value type
       ``V`` in ``dict[K, V]``.
   * - ``OptionalDeff``
     - ``_element``
     - Single child describing the wrapped type ``T`` in ``Optional[T]``.
   * - ``FieldsDeff``
     - *(leaf — none)*
     - Primitive ctypes field.
   * - ``StringDeff``
     - *(leaf — none)*
     - ``str`` field.
   * - ``BytesDeff``
     - *(leaf — none)*
     - ``bytes`` field.

Declaration Order is Canonical
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``struct_parser`` collects annotations with :func:`typing.get_type_hints`.
In Python 3.7+, ``__annotations__`` is an ordered dict that preserves the
**source-code declaration order** of each class body.  That order flows
directly into the child list of every ``ObjectDeff`` node and is never
reordered.

**Consequence:** reordering fields in the class body changes the schema hash
*and* the byte layout of every frame produced from that struct.  Encoder and
decoder must use the identical declaration order — any divergence is detected
by the hash check and raises :exc:`InvalidHeaderException`.

Depth-First, Left-to-Right Traversal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both the encoder and decoder walk the typing tree **depth-first,
left-to-right** (i.e. children are visited in insertion order).  Leaf nodes
emit or consume bytes directly; container nodes emit or consume a
count/presence prefix and then recurse into their child nodes:

* **ObjectDeff** — no wrapper bytes; visits each child field in declaration
  order.
* **ListDeff** — emits/reads the element count, then visits ``_element`` once
  per logical entry (index 0, 1, 2 …).
* **HashmapDeff** — emits/reads the entry count, then for each entry visits
  ``_key`` immediately followed by ``_value``.
* **OptionalDeff** — emits/reads the 1-byte presence flag, then visits
  ``_element`` only when the flag is ``0x01``.

Example Tree
~~~~~~~~~~~~~

Given:

.. code-block:: python

    from dataclasses import dataclass

    @dataclass
    class Inner:
        x: float
        y: float

    @dataclass
    class Outer:
        a: int
        b: str
        nested: Inner
        items: list[float]

``struct_parser(Outer)`` produces:

.. code-block:: text

    ObjectDeff("Outer")
    ├── FieldsDeff("a")             ← encoded/decoded 1st
    ├── StringDeff("b")             ← encoded/decoded 2nd
    ├── ObjectDeff("nested")        ← encoded/decoded 3rd (inline, no wrapper)
    │   ├── FieldsDeff("x")         ├── encoded/decoded 3a
    │   └── FieldsDeff("y")         └── encoded/decoded 3b
    └── ListDeff("items")           ← encoded/decoded 4th
        └── FieldsDeff("_element")      element-type descriptor (applied per entry)

The resulting byte stream visits fields in the order: ``a``, ``b``,
``nested.x``, ``nested.y``, count-of-items, ``items[0]``, ``items[1]``, …

----

Payload Encoding
----------------

Fields are encoded **in declaration order** as established by the parsing
tree (see `Parsing Tree and Traversal Order`_ above), concatenated with no
padding, alignment gaps, or separators between them.

Primitives
~~~~~~~~~~

Primitive fields (``bool``, ``int``, ``float``, and their ctypes variants) are
encoded with Python's ``struct.pack`` using the field's format token. The
endianness prefix in the token is ``">"`` (big-endian) or ``"<"``
(little-endian) depending on the ``IS_LITTLE_ENDIAN`` flag.

.. list-table::
   :header-rows: 1
   :widths: 30 15 10 10

   * - Python / ctypes type
     - struct token
     - Bytes
     - Signed
   * - ``bool`` / ``ctypes.c_bool``
     - ``?``
     - 1
     - —
   * - ``ctypes.c_int8``
     - ``b``
     - 1
     - Yes
   * - ``ctypes.c_uint8``
     - ``B``
     - 1
     - No
   * - ``ctypes.c_int16``
     - ``h``
     - 2
     - Yes
   * - ``ctypes.c_uint16``
     - ``H``
     - 2
     - No
   * - ``ctypes.c_int32`` / ``ctypes.c_int``
     - ``i``
     - 4
     - Yes
   * - ``ctypes.c_uint32`` / ``ctypes.c_uint``
     - ``I``
     - 4
     - No
   * - ``int`` / ``ctypes.c_int64`` / ``ctypes.c_longlong``
     - ``q``
     - 8
     - Yes
   * - ``ctypes.c_uint64`` / ``ctypes.c_ulonglong``
     - ``Q``
     - 8
     - No
   * - ``ctypes.c_float``
     - ``f``
     - 4
     - —
   * - ``float`` / ``ctypes.c_double``
     - ``d``
     - 8
     - —

Strings (``str``)
~~~~~~~~~~~~~~~~~

.. code-block:: text

    ┌──────────────────────────────┬────────────────────────────┐
    │   Length  (uint32 or uint64) │  UTF-8 encoded content     │
    │   4 or 8 bytes               │  <Length> bytes            │
    └──────────────────────────────┴────────────────────────────┘

1. The string is encoded to UTF-8.
2. A length prefix (number of **bytes**, not characters) is written: ``uint32``
   (4 bytes) by default, or ``uint64`` (8 bytes) when ``IS_LENGTH_64_BYTES`` is
   set.
3. The UTF-8 bytes follow immediately.

The length prefix respects the ``IS_LITTLE_ENDIAN`` flag.

Bytes (``bytes``)
~~~~~~~~~~~~~~~~~

Identical structure to ``str``, but no text encoding step — the raw bytes are
written after the length prefix (``uint32`` by default, ``uint64`` when
``IS_LENGTH_64_BYTES`` is set).

.. code-block:: text

    ┌──────────────────────────────┬──────────────────────────┐
    │   Length  (uint32 or uint64) │  Raw bytes               │
    │   4 or 8 bytes               │  <Length> bytes          │
    └──────────────────────────────┴──────────────────────────┘

Lists (``list[T]``)
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    ┌──────────────────────────────┬──────────────┬─────────────┬────────┐
    │  Count  (uint32 or uint64)   │  Element 0   │  Element 1  │  …     │
    │  4 or 8 bytes                │  (variable)  │  (variable) │        │
    └──────────────────────────────┴──────────────┴─────────────┴────────┘

1. An element count is written: ``uint32`` (4 bytes) by default, or ``uint64``
   (8 bytes) when ``IS_LENGTH_64_BYTES`` is set.
2. Each element is encoded using the encoder for its type ``T``.

There is no element-separator; offsets are derived by decoding each element
in sequence. The count prefix respects the ``IS_LITTLE_ENDIAN`` flag.

Optionals (``Optional[T]`` / ``T | None``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    ┌─────────────────────┐
    │ Present?  (bool, 1B)│   →  False
    └─────────────────────┘

    ┌─────────────────────┬─────────────────────────────────┐
    │ Present?  (bool, 1B)│  Encoded value  (variable)      │
    │  True               │                                 │
    └─────────────────────┴─────────────────────────────────┘

A ``None`` value occupies exactly **1 byte** (the presence flag ``0x00``). A
non-``None`` value occupies 1 byte plus whatever the encoded value requires.

Dicts (``dict[K, V]``)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    ┌──────────────────────────────┬───────────────┬───────────────┬──────────────┬──────────────┬────────┐
    │  Count  (uint32 or uint64)   │  Key 0        │  Value 0      │  Key 1       │  Value 1     │  …     │
    │  4 or 8 bytes                │  (variable)   │  (variable)   │  (variable)  │  (variable)  │        │
    └──────────────────────────────┴───────────────┴───────────────┴──────────────┴──────────────┴────────┘

1. A ``uint32`` entry count is written (``uint64`` when ``IS_LENGTH_64_BYTES`` is set).
2. For each entry, the key is encoded using the encoder for type ``K``, followed
   immediately by the value encoded using the encoder for type ``V``.

There is no entry separator; offsets are derived by decoding each key-value pair
in sequence. Both ``K`` and ``V`` may be any supported type, including nested
objects or other variable-length types. The count prefix respects the
``IS_LITTLE_ENDIAN`` flag.

Nested Objects
~~~~~~~~~~~~~~

Nested annotated classes have no wrapper of their own — their fields are simply
encoded in declaration order and concatenated inline. Nesting is handled
recursively by the ``ObjectEncoder``.

.. code-block:: text

    ┌──────────────────────────────────────────────────────────────────┐
    │  Outer.field_a  │  Outer.field_b  │ Outer.nested.x │ …          │
    │  (encoded)      │  (encoded)      │ (encoded)      │            │
    └──────────────────────────────────────────────────────────────────┘

----

Schema Compatibility Rules
---------------------------

When you call :func:`unpack`, the library computes the expected hash from the
target Python class and compares it to the hash in the buffer. The rules are:

* **Version mismatch** → :exc:`InvalidHeaderException` (protocol incompatibility).
* **Hash mismatch** → :exc:`InvalidHeaderException` (schema drift — the buffer
  was encoded from a different struct layout).
* **Match** → decoding proceeds.

There is intentionally no partial-decode or best-effort mode. Either the schema
matches exactly, or the data is rejected. This keeps cross-language consumers safe.

----

Worked Example
--------------

Encoding a small ``Point`` struct with default options:

.. code-block:: python

    from dataclasses import dataclass
    from compacto import pack, inspect

    @dataclass
    class Point:
        x: float   # c_double, 8 bytes
        y: float   # c_double, 8 bytes

    data = pack(Point(1.0, -2.5))

The resulting buffer (24 bytes total):

.. code-block:: text

    Offset  Bytes          Description
    ──────  ─────────────  ──────────────────────────────────────────
    0x00    00 00          Options = 0x0000  (NONE, big-endian payload)
    0x02    01 00          Version = 0x0100  (major=1, revision=0)
    0x04    ?? ?? ?? ??    Schema Hash (4 bytes, BLAKE2b)
    0x08    3F F0 00 00    x = 1.0  (IEEE 754 double, big-endian)
            00 00 00 00
    0x10    C0 04 00 00    y = -2.5 (IEEE 754 double, big-endian)
            00 00 00 00

Same struct encoded with ``is_little_endian=True``:

.. code-block:: text

    Offset  Bytes          Description
    ──────  ─────────────  ──────────────────────────────────────────
    0x00    00 01          Options = 0x0001  (IS_LITTLE_ENDIAN)
    0x02    01 00          Version = 0x0100  (header still big-endian!)
    0x04    ?? ?? ?? ??    Schema Hash (4 bytes, same hash)
    0x08    00 00 00 00    x = 1.0  (IEEE 754 double, little-endian)
            00 00 F0 3F
    0x10    00 00 00 00    y = -2.5 (IEEE 754 double, little-endian)
            00 00 04 C0

Note: the hash is identical in both cases because the schema has not changed.

----

Implementing a Reader in Another Language
------------------------------------------

Minimum steps to decode a compacto frame:

1. Read bytes 0–1 as a big-endian ``uint16`` → ``options``.
2. Read bytes 2–3 as a big-endian ``uint16`` → ``version``. Check against your
   expected version.
3. If ``options & 0x0002`` (``IS_8_BYTE_HASH``): read 8 bytes → ``schema_hash``,
   payload starts at byte 12.
   Otherwise: read 4 bytes → ``schema_hash``, payload starts at byte 8.
4. Optionally verify ``schema_hash`` against your pre-computed value for the
   target struct.
5. If ``options & 0x0001`` (``IS_LITTLE_ENDIAN``): decode payload fields as
   little-endian. Otherwise use big-endian.
5a. If ``options & 0x0004`` (``IS_LENGTH_64_BYTES``): length prefixes for
   ``str``, ``bytes``, ``list``, and ``dict`` fields are ``uint64`` (8 bytes).
   Otherwise they are ``uint32`` (4 bytes).
6. Decode each field following the depth-first, left-to-right traversal
   described in `Parsing Tree and Traversal Order`_.  The canonical field
   sequence is the **declaration order** of each class body, applied
   recursively:

   * **Fixed-size primitive** — read *N* bytes and interpret as the appropriate
     integer or float type.
   * **str / bytes** — read a ``uint32`` length (or ``uint64`` if
     ``IS_LENGTH_64_BYTES``), then read that many bytes. Interpret as UTF-8 for
     ``str``.
   * **list[T]** — read a ``uint32`` count (or ``uint64`` if
     ``IS_LENGTH_64_BYTES``), then decode *count* elements of type ``T`` in
     sequence (left to right, index 0 first).
   * **dict[K, V]** — read a ``uint32`` count (or ``uint64`` if
     ``IS_LENGTH_64_BYTES``), then decode *count* key-value pairs: for each
     pair, decode one ``K`` followed immediately by one ``V`` (key before
     value, pairs in insertion order).
   * **Optional[T]** — read 1 byte (the presence flag). If ``0x01``, decode one
     value of type ``T``. If ``0x00``, the field is ``null`` / ``None``.
   * **Nested object** — no wrapper bytes; decode its fields inline, in their
     own declaration order, before continuing to the next field of the parent.