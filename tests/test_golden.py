import hashlib
import io

from veriproof.data.render import render_chat
from veriproof.data.tamper import apply_copy_move


def _png_sha(img):
    b = io.BytesIO()
    img.save(b, "PNG")
    return hashlib.sha256(b.getvalue()).hexdigest()


def test_render_golden_hash():
    assert _png_sha(render_chat(42)) == _png_sha(render_chat(42))
    assert _png_sha(render_chat(42)) == "01ef035f091458336774d7802c3cae787cd12615aa95fbb4f5492bdbdbd77061"


def test_tamper_golden_hash():
    img, mask = apply_copy_move(render_chat(7), 1)
    assert _png_sha(img) == "419cc14dc1b8a2cdb1c8a7d2a71af601fc73f89eaebd1ddc11936003889f24e0"
    assert mask.sum() > 0
