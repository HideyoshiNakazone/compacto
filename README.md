# compacto

> A Python library for binary serialization of structured data using type annotations — inspired by C structs.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Coverage](https://codecov.io/gh/HideyoshiNakazone/compacto/branch/main/graph/badge.svg)](Coverage)

---

## Overview

**compacto** turns Python objects into compact binary data and back, using type annotations to drive the encoding/decoding process — no schemas, no decorators, just plain annotated classes.

It leverages Python's `struct` module for fixed-size primitive types. All fields must be fully annotated and use supported types — unsupported types raise a `TypeError` at encode time, keeping the output strictly cross-language compatible.

---

## Installation

```bash
pip install compacto
```

Or with `uv`:

```bash
uv add compacto
```

---

## Quick Start

```python
from dataclasses import dataclass
from compacto import pack, unpack

@dataclass
class Point:
    x: float
    y: float

p = Point(1.5, 2.7)

data = pack(p)           # bytes
result = unpack(Point, data)

assert result.x == p.x
assert result.y == p.y
```

---

## Supported Types

| Python Type        | Default Encoding                         |
|--------------------|------------------------------------------|
| `bool`             | 1-byte boolean                           |
| `int`              | 64-bit signed (`long long`)              |
| `float`            | 64-bit double                            |
| `str`              | Length-prefixed UTF-8                    |
| `bytes`            | Length-prefixed raw bytes                |
| `list[T]`          | Length-prefixed sequence of `T`          |
| `Optional[T]`      | 1-byte presence flag + encoded `T`       |
| Annotated class    | Recursively encoded fields in order      |

---

## Precision Control via ctypes Annotations

By default, `int` is encoded as a 64-bit signed integer and `float` as a 64-bit double. You can override this per-field using `Annotated` with a `ctypes` type to control the exact binary representation:

```python
from dataclasses import dataclass
from typing_extensions import Annotated
import ctypes
from compacto import pack, unpack

@dataclass
class Measurement:
    small:   Annotated[int, ctypes.c_int16]    # 2 bytes
    medium:  Annotated[int, ctypes.c_int32]    # 4 bytes
    precise: Annotated[float, ctypes.c_float]  # 4 bytes (single precision)

obj = Measurement(42, 100000, 3.14)
data = pack(obj)
result = unpack(Measurement, data)
```

### Permitted ctypes

| ctypes type         | Python type | Size    | Signed |
|---------------------|-------------|---------|--------|
| `ctypes.c_bool`     | `bool`      | 1 byte  | —      |
| `ctypes.c_int8`     | `int`       | 1 byte  | Yes    |
| `ctypes.c_int16`    | `int`       | 2 bytes | Yes    |
| `ctypes.c_int32`    | `int`       | 4 bytes | Yes    |
| `ctypes.c_int64`    | `int`       | 8 bytes | Yes    |
| `ctypes.c_uint8`    | `int`       | 1 byte  | No     |
| `ctypes.c_uint16`   | `int`       | 2 bytes | No     |
| `ctypes.c_uint32`   | `int`       | 4 bytes | No     |
| `ctypes.c_uint64`   | `int`       | 8 bytes | No     |
| `ctypes.c_int`      | `int`       | 4 bytes | Yes    |
| `ctypes.c_uint`     | `int`       | 4 bytes | No     |
| `ctypes.c_float`    | `float`     | 4 bytes | —      |
| `ctypes.c_double`   | `float`     | 8 bytes | —      |

> The annotation must be the ctypes **class**, not an instance. `Annotated[int, ctypes.c_int32]` is valid; `Annotated[int, ctypes.c_int32()]` raises `TypeParsingException`.

---

## Nested Objects

compacto handles nested annotated classes out of the box:

```python
from dataclasses import dataclass
from compacto import pack, unpack

@dataclass
class Address:
    street: str
    number: int

@dataclass
class Person:
    name: str
    age: int
    address: Address

person = Person("Alice", 30, Address("Main St", 42))

data = pack(person)
result = unpack(Person, data)

assert result.name == person.name
assert result.address == person.address
```

---

## Optional Fields

Fields annotated with `Optional[T]` (or `T | None`) are encoded with a 1-byte presence flag followed by the encoded value when present:

```python
from dataclasses import dataclass
from typing import Optional
from compacto import pack, unpack

@dataclass
class Profile:
    username: str
    bio: Optional[str]

p = Profile("alice", None)
data = pack(p)
result = unpack(Profile, data)

assert result.username == p.username
assert result.bio is None
```

---

## Lists

Lists of any supported type are handled transparently:

```python
@dataclass
class Inventory:
    items:      list[str]
    quantities: list[int]

inv = Inventory(["sword", "shield"], [3, 1])
data = pack(inv)
result = unpack(Inventory, data)

assert result.items == inv.items
```

---

## Endianness Control

By default the payload is encoded in **big-endian** byte order. Pass `is_little_endian=True` to `pack()` to switch to little-endian. The header is always big-endian regardless of this setting — see [Wire Protocol](#wire-protocol) for details.

```python
data = pack(obj, is_little_endian=True)
result = unpack(MyClass, data)  # endianness is embedded in the header
```

---

## API

### `pack(obj, **options) -> bytes`

Serializes an annotated object to bytes. Returns a buffer containing a binary header followed by the encoded payload.

```python
data: bytes = pack(obj)
data: bytes = pack(obj, is_little_endian=True)
data: bytes = pack(obj, is_8_byte_hash=True)
data: bytes = pack(obj, is_length_64_bytes=True)
```

**Options:**

| Option                | Type   | Default | Description                                                       |
|-----------------------|--------|---------|-------------------------------------------------------------------|
| `is_little_endian`    | `bool` | `False` | Encode payload in little-endian byte order                        |
| `is_8_byte_hash`      | `bool` | `False` | Use an 8-byte schema hash instead of 4-byte                       |
| `is_length_64_bytes`  | `bool` | `False` | Use `uint64` length prefixes for `str`, `bytes`, and `list` fields |

### `unpack(clzz, data) -> T`

Deserializes bytes into an instance of `clzz`. Validates the protocol version and schema hash embedded in the header before decoding — raises `InvalidHeaderException` on any mismatch.

```python
obj = unpack(MyClass, data)
```

Endianness is read from the header; the caller does not need to specify it.

### `inspect(pos_data) -> EncodingHeader`

Returns the encoding header for a type or for already-encoded bytes. Useful for verifying schema compatibility without fully deserializing.

```python
from compacto import inspect

# From a type — computes what the header would look like
header = inspect(Point)
print(header.version)      # 1
print(header.schema_hash.hex())

# From encoded bytes — decodes the actual header
data = pack(Point(1.0, 2.0))
header = inspect(data)
print(header.options)      # OptionFlags.NONE
```

**Returns** an `EncodingHeader` with fields:

| Field         | Type          | Description                             |
|---------------|---------------|-----------------------------------------|
| `options`     | `OptionFlags` | Bitmask of encoding options             |
| `version`     | `int`         | Protocol version (`0x0100` = major 1, revision 0) |
| `schema_hash` | `bytes`       | BLAKE2b fingerprint of the struct layout|

---

## Wire Protocol

Every `pack()` call produces a buffer with this layout:

```
+------------------+------------------+--------------------+--------------------+
|  Options         |  Version         |  Schema Hash       |  Payload           |
+------------------+------------------+--------------------+--------------------+
|  uint16 (2 B)    |  uint16 (2 B)    |  4 B or 8 B        |  variable          |
+------------------+------------------+--------------------+--------------------+
  bytes 0–1          bytes 2–3          bytes 4–7 (or 4–11)   bytes 8+ (or 12+)
```

**The header is always big-endian.** This lets the decoder read options and version deterministically without knowing the payload byte order in advance.

### Options flags

| Bit | Hex    | Name                 | Effect                                                         |
|-----|--------|----------------------|----------------------------------------------------------------|
| 0   | `0x01` | `IS_LITTLE_ENDIAN`   | Payload encoded in little-endian byte order                    |
| 1   | `0x02` | `IS_8_BYTE_HASH`     | Schema hash is 8 bytes instead of 4                            |
| 2   | `0x04` | `IS_LENGTH_64_BYTES` | Length prefixes for `str`, `bytes`, and `list` use `uint64` instead of `uint32` |

### Schema hash

The hash is a BLAKE2b digest of the struct's typing tree, computed over:
- The type-definition class name at each node
- The field name at each node
- The ctypes implementation type for primitive fields

This fingerprint lets `unpack()` detect schema drift at the boundary. If a field is renamed, reordered, or its type changed, the hash will not match and `InvalidHeaderException` is raised before any bytes are decoded.

### Payload encoding

Fields are encoded in declaration order, concatenated with no padding or separators:

| Type               | Encoding                                                      |
|--------------------|---------------------------------------------------------------|
| Primitive (`int`, `float`, `bool`, ctypes variants) | `struct.pack` with the field's format token |
| `str`              | `uint64` length (bytes) followed by UTF-8 content            |
| `bytes`            | `uint64` length followed by raw bytes                        |
| `list[T]`          | `uint64` element count followed by each element encoded      |
| `Optional[T]`      | `bool` presence flag; if `True`, followed by encoded `T`     |
| Nested object      | All fields of the nested object encoded recursively in order  |

The `uint64` length fields for `str`, `bytes`, and `list` respect the `IS_LITTLE_ENDIAN` flag.

---

## Exceptions

All compacto exceptions extend `InternalException` and a standard Python base:

| Exception              | Base                       | Raised when                                           |
|------------------------|----------------------------|-------------------------------------------------------|
| `TypeParsingException` | `TypeError`                | An annotation is invalid or the type is unsupported   |
| `EncodingException`    | `ValueError`               | An error occurs during encoding                       |
| `DecodingException`    | `ValueError`               | An error occurs during decoding                       |
| `InvalidHeaderException` | `RuntimeError`           | Header version or schema hash does not match          |
| `AssertionException`   | `AssertionError`           | An internal invariant is violated                     |

```python
from compacto import pack, unpack
from compacto.utils.exceptions import InvalidHeaderException

try:
    result = unpack(MyClass, stale_data)
except InvalidHeaderException as e:
    print(f"Schema mismatch: {e}")
```

---

## How It Works

1. **Struct parsing** — compacto inspects the type annotations of your class and builds a typed tree of field definitions. Each node in the tree carries the field name, its resolved type, and its ctypes implementation where applicable.
2. **Header construction** — a BLAKE2b hash of the typing tree is computed and written to the header alongside the protocol version and option flags.
3. **Encoding** — each field is encoded by the appropriate encoder (`FieldEncoder` for primitives, `StringEncoder`, `ByteEncoder`, `ListEncoder`, `OptionalEncoder`, `ObjectEncoder`) and the results are concatenated in declaration order.
4. **Decoding** — `unpack()` first reads the header, validates version and schema hash against the target class, then walks the same typing tree to decode each field at the correct byte offset.

---

## Size Comparison

| Format                        | Size     |
|-------------------------------|----------|
| compacto (ctypes annotations) | 14 bytes |
| compacto (default precision)  | 20 bytes |
| pickle                        | 60 bytes |

> Note: pickle is not compacto's real competition — compacto targets fixed-schema, cross-language binary serialization where output size and type strictness matter. Think C structs over the wire, not Python object persistence.

<details>
<summary>Show benchmark code</summary>

```python
import ctypes
import pickle
from dataclasses import dataclass
from typing_extensions import Annotated
from compacto import pack

@dataclass
class Data1:
    a: Annotated[int, ctypes.c_int16]
    b: Annotated[float, ctypes.c_float]

@dataclass
class Data2:
    a: int
    b: float

obj1 = Data1(42, 3.14)
obj2 = Data2(42, 3.14)

data1 = pack(obj1)
data2 = pack(obj2)
data_pickled = pickle.dumps(obj1)

print(f"compacto (annotated): {len(data1)} bytes")
print(f"compacto (default):   {len(data2)} bytes")
print(f"pickle:               {len(data_pickled)} bytes")
```

</details>

---

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run poe tests

# Type checking
uv run poe type-check
```

---

## Roadmap

- [ ] `Dict` — encode dicts as a array of key-value pairs with length prefix (c implementation can use [stb_ds.h](https://github.com/nothings/stb/blob/master/stb_ds.h))

---

## License

MIT — see [LICENSE](LICENSE).