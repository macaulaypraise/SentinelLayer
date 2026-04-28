import pytest

from app.core.camara.client import normalise


def test_nigerian_number_normalised() -> None:
    assert normalise("+2348012345678") == "+2348012345678"


def test_local_format_normalised() -> None:
    assert normalise("08012345678") == "+2348012345678"


def test_invalid_number_raises() -> None:
    with pytest.raises(ValueError):
        normalise("00000")
