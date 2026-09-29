# tests/test_launder.py
import pytest
from PIL import Image

from veriproof.data.launder import apply_launder


def _img():
    return Image.new("RGB", (640, 640), (120, 40, 200))

def test_empty_chain_unchanged():
    img = _img()
    out, chain = apply_launder(img, [])
    assert chain == "none"
    assert out.tobytes() == img.tobytes()

def test_jpeg85_changes_and_marks_chain():
    out, chain = apply_launder(_img(), ["jpeg85"])
    assert chain == "jpeg85"
    assert out.size == (640, 640)

def test_unknown_op_raises():
    with pytest.raises(ValueError):
        apply_launder(_img(), ["not_an_op"])
