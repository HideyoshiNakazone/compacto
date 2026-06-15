from compacto.encoding.hashmap_parser import HashmapEncoder
from compacto.struct_parser import struct_parser

from dataclasses import dataclass


class TestHashmapEncoding:
    def test_encoder_decoder_with_dict_str_int(self) -> None:
        obj_deff = struct_parser(dict[str, int])

        test_obj = {
            "a": 1,
            "b": 2,
            "c": 3,
        }

        data = HashmapEncoder.encode(obj_deff, test_obj)
        decoded_obj, offset = HashmapEncoder.decode(obj_deff, data)

        assert test_obj == decoded_obj

    def test_encoder_decoder_with_dict_str_clzz(self) -> None:
        @dataclass
        class DataWrapper:
            a: int

        obj_deff = struct_parser(dict[str, DataWrapper])

        test_obj = {
            "a": DataWrapper(1),
            "b": DataWrapper(2),
            "c": DataWrapper(3),
        }

        data = HashmapEncoder.encode(obj_deff, test_obj)
        decoded_obj, offset = HashmapEncoder.decode(obj_deff, data)

        assert test_obj == decoded_obj
