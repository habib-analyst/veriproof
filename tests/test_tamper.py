import numpy as np
import pytest

from veriproof.data.render import render_chat
from veriproof.data.tamper import (
    TAMPER_OPS,
    apply_copy_move,
    apply_inpaint,
    apply_splice,
    apply_text_edit,
)


def test_all_ops_return_valid_masks():
    img = render_chat(7)
    donor = render_chat(8)
    results = {
        "copy_move": apply_copy_move(img, 1),
        "splice": apply_splice(img, donor, 1),
        "text_edit": apply_text_edit(img, 1),
        "inpaint": apply_inpaint(img, 1),
    }
    assert set(results) == set(TAMPER_OPS)
    for name, (out, mask) in results.items():
        assert out.size == img.size, name
        assert mask.shape == (img.size[1], img.size[0]), name
        assert mask.dtype == np.uint8, name
        assert set(np.unique(mask)) <= {0, 1}, name
        assert mask.sum() > 0, name


def test_splice_rejects_mismatched_donor():
    img = render_chat(7)
    donor = render_chat(8).resize((540, 960))
    with pytest.raises(ValueError):
        apply_splice(img, donor, 1)
