import struct


def safe_calcsize(token, fallback=None):
    try:
        return struct.calcsize(token)
    except struct.error as e:
        if fallback is None:
            raise e
        return fallback


# Type Tokens
BYTE_TYPE_TOKEN = "x"
CHAR_TYPE_TOKEN = "c"
SIGNED_CHAR_TYPE_TOKEN = "b"
UNSIGNED_CHAR_TYPE_TOKEN = "B"
BOOL_TYPE_TOKEN = "?"
SHORT_TYPE_TOKEN = "h"
UNSIGNED_SHORT_TYPE_TOKEN = "H"
INT_TYPE_TOKEN = "i"
UNSIGNED_INT_TYPE_TOKEN = "I"
LONG_TYPE_TOKEN = "l"
UNSIGNED_LONG_TYPE_TOKEN = "L"
LONG_LONG_TYPE_TOKEN = "q"
UNSIGNED_LONG_LONG_TYPE_TOKEN = "Q"
SSIZE_T_TYPE_TOKEN = "n"
SIZE_T_TYPE_TOKEN = "N"
FLOAT16_TYPE_TOKEN = "e"
FLOAT_TYPE_TOKEN = "f"
DOUBLE_TYPE_TOKEN = "d"
FLOAT_COMPLEX_TYPE_TOKEN = "F"
DOUBLE_COMPLEX_TYPE_TOKEN = "D"
VOID_PTR_TYPE_TOKEN = "P"

# Fixed and System-Dependent C Type Sizes via calcsize
SIZE_PAD_BYTE = safe_calcsize(BYTE_TYPE_TOKEN)
SIZE_CHAR = safe_calcsize(CHAR_TYPE_TOKEN)
SIZE_SIGNED_CHAR = safe_calcsize(SIGNED_CHAR_TYPE_TOKEN)
SIZE_UNSIGNED_CHAR = safe_calcsize(UNSIGNED_CHAR_TYPE_TOKEN)
SIZE_BOOL = safe_calcsize(BOOL_TYPE_TOKEN)
SIZE_SHORT = safe_calcsize(SHORT_TYPE_TOKEN)
SIZE_UNSIGNED_SHORT = safe_calcsize(UNSIGNED_SHORT_TYPE_TOKEN)
SIZE_INT = safe_calcsize(INT_TYPE_TOKEN)
SIZE_UNSIGNED_INT = safe_calcsize(UNSIGNED_INT_TYPE_TOKEN)
SIZE_LONG = safe_calcsize(LONG_TYPE_TOKEN)
SIZE_UNSIGNED_LONG = safe_calcsize(UNSIGNED_LONG_TYPE_TOKEN)
SIZE_LONG_LONG = safe_calcsize(LONG_LONG_TYPE_TOKEN)
SIZE_UNSIGNED_LONG_LONG = safe_calcsize(UNSIGNED_LONG_LONG_TYPE_TOKEN)
SIZE_SSIZE_T = safe_calcsize(SSIZE_T_TYPE_TOKEN)
SIZE_SIZE_T = safe_calcsize(SIZE_T_TYPE_TOKEN)
SIZE_FLOAT16 = safe_calcsize(FLOAT16_TYPE_TOKEN)
SIZE_FLOAT = safe_calcsize(FLOAT_TYPE_TOKEN)
SIZE_DOUBLE = safe_calcsize(DOUBLE_TYPE_TOKEN)
SIZE_FLOAT_COMPLEX = safe_calcsize(FLOAT_COMPLEX_TYPE_TOKEN, safe_calcsize("f") * 2)
SIZE_DOUBLE_COMPLEX = safe_calcsize(DOUBLE_COMPLEX_TYPE_TOKEN, safe_calcsize("d") * 2)
SIZE_VOID_PTR = safe_calcsize(VOID_PTR_TYPE_TOKEN)
