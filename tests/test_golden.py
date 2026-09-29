import hashlib

from veriproof.data.render import render_chat
from veriproof.data.tamper import apply_copy_move


def _pixels_sha(img):
    # Raw pixels, not encoded bytes: PNG/JPEG compression output varies with
    # zlib/libjpeg versions across platforms, pixel buffers do not.
    return hashlib.sha256(img.tobytes()).hexdigest()


def test_render_golden_hash():
    assert _pixels_sha(render_chat(42)) == _pixels_sha(render_chat(42))
    assert _pixels_sha(render_chat(42)) == "7b6a416461cc15b3b965ccf4f0e5f8424bfc2dd17decb76275dbbd6b13cbd3e7"


def test_tamper_golden_hash():
    img, mask = apply_copy_move(render_chat(7), 1)
    assert _pixels_sha(img) == "cdf51b2c7fa0778f35861a08dabac203dd603c0aed1a1ca6b4bf9ba994ae0e42"
    assert mask.sum() > 0
