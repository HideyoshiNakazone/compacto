class InternalException(Exception):
    message: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    @property
    def cause(self):
        return self.__cause__ or self.__context__


class AssertionException(InternalException, AssertionError): ...


class TypeParsingException(InternalException, TypeError): ...


class EncodingException(InternalException, ValueError): ...


class DecodingException(InternalException, ValueError): ...


class InvalidHeaderException(InternalException, RuntimeError): ...
