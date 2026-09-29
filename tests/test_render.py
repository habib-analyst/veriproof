import io

from veriproof.data.render import render_chat, render_payment


def test_render_deterministic():
    a, b = render_chat(42), render_chat(42)
    buf_a, buf_b = io.BytesIO(), io.BytesIO()
    a.save(buf_a, "PNG")
    b.save(buf_b, "PNG")
    assert buf_a.getvalue() == buf_b.getvalue()
    p, q = render_payment(42), render_payment(42)
    buf_p, buf_q = io.BytesIO(), io.BytesIO()
    p.save(buf_p, "PNG")
    q.save(buf_q, "PNG")
    assert buf_p.getvalue() == buf_q.getvalue()

def test_render_varied_and_correct_size():
    imgs = [render_chat(i) for i in range(3)] + [render_payment(i) for i in range(3)]
    assert all(im.size == (1080, 1920) for im in imgs)
    bufs = []
    for im in imgs:
        b = io.BytesIO()
        im.save(b, "PNG")
        bufs.append(b.getvalue())
    assert len(set(bufs)) == 6
