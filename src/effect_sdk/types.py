from pyntelope.types.base import Composte, Primitive

class Variant(Composte):
    value: bytes
    idx: int

    @classmethod
    def from_dict(cls, d: dict, /, types_):
        type_ = d[0]
        value = d[1]
        idx = types_.index(type_)
        return cls(value=bytes(value), idx=idx)


    def __bytes__(self):
        """Convert instance to bytes."""
        bytes_ = b""
        bytes_ += bytes([self.idx])
        bytes_ += self.value
        return bytes_

    @classmethod
    def from_bytes(cls, bytes_: bytes, /, type_=type):
        """Create instance from bytes."""
        return None

class Struct(Primitive):
    value: tuple

    def __bytes__(self):
        """Convert instance to bytes."""
        bytes_ = b''
        for v in self.value:
            bytes_ += bytes(v)
        return bytes_

    @classmethod
    def from_bytes(cls, bytes_: bytes, /, type_=type):
        """Create instance from bytes."""
        return None
