# compacto

> A Python library for binary serialization of structured data using type annotations — inspired by C structs.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

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

| Python Type | Encoding         |
|-------------|------------------|
| `int`       | 64-bit signed (`long long`) |
| `float`     | 64-bit double    |
| `bool`      | 1-byte boolean   |
| `str`       | Length-prefixed UTF-8 |
| `bytes`     | Length-prefixed raw bytes |
| `list[T]`   | Length-prefixed sequence of `T` |
| `Optional[T]` | 1-byte presence flag + encoded `T` when present |
| Annotated class | Recursively encoded fields |

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
    items: list[str]
    quantities: list[int]

inv = Inventory(["sword", "shield"], [3, 1])
data = pack(inv)
result = unpack(Inventory, data)

assert result.items == inv.items
```

---

## API

### `pack(obj) -> bytes`

Serializes an annotated object to bytes.

```python
data: bytes = pack(obj)
```

### `unpack(clzz, data) -> T`

Deserializes bytes into an instance of `clzz`. Returns the unpacked data`.

```python
obj = unpack(MyClass, data)
```

---

## How It Works

1. **Struct parsing** — compacto inspects the type annotations of your class and builds a typed tree of fields.
2. **Encoding** — each field is encoded using the appropriate encoder (int, float, str, Optional, etc.).
3. **Strict** — unsupported types (e.g. `dict`, unannotated classes) raise a `TypeError`, ensuring the output is always cross-language compatible.

---

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run poe tests
```

---

## Roadmap

- [ ] `Enum` — encode as underlying integer value for cross-language compatibility
- [ ] Endianness control — allow specifying byte order (big/little/native) for cross-language interop
- [ ] Magic bytes / format version header — safe cross-language deserialization

---

## License

MIT — see [LICENSE](LICENSE).
