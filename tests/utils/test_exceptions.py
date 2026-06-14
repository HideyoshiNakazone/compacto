from compacto.utils.exceptions import (
    AssertionException,
    DecodingException,
    EncodingException,
    InternalException,
    InvalidHeaderException,
    TypeParsingException,
)


class TestInternalException:
    def test_cause_is_none_when_no_chain(self) -> None:
        exc = InternalException("test message")
        assert exc.cause is None

    def test_cause_returns_explicit_chain(self) -> None:
        original = ValueError("root cause")
        try:
            try:
                raise original
            except ValueError as e:
                raise InternalException("wrapped") from e
        except InternalException as exc:
            assert exc.cause is original

    def test_cause_returns_implicit_context(self) -> None:
        original = ValueError("context error")
        try:
            try:
                raise original
            except ValueError:
                raise InternalException("wrapped")
        except InternalException as exc:
            assert exc.cause is original

    def test_message_is_stored(self) -> None:
        exc = InternalException("hello")
        assert exc.message == "hello"

    def test_subclasses_are_also_base_exceptions(self) -> None:
        assert issubclass(AssertionException, (InternalException, AssertionError))
        assert issubclass(TypeParsingException, (InternalException, TypeError))
        assert issubclass(EncodingException, (InternalException, ValueError))
        assert issubclass(DecodingException, (InternalException, ValueError))
        assert issubclass(InvalidHeaderException, (InternalException, RuntimeError))
