# -*- coding:utf-8 -*-

from blockdiag.drawer import DiagramDraw
from blockdiag.utils import XY


class MockDrawer(object):
    def __init__(self):
        self.calls = []

    def line(self, *args, **kwargs):
        self.calls.append(("line", args, kwargs))

    def arc(self, *args, **kwargs):
        self.calls.append(("arc", args, kwargs))


def _draw_lines(line, radius, expected_calls, **kwargs):
    drawer = MockDrawer()
    DiagramDraw.line(drawer, line, radius, **kwargs)
    assert drawer.calls == expected_calls, \
        "expected:%r\nactual:%r" % (expected_calls, drawer.calls)


def xys(*args):
    # (a, b, c, d, ...) -> (XY(a, b), XY(c, d), ...)
    def _():
        for i in range(0, len(args), 2):
            yield XY(args[i], args[i + 1])
    return tuple(_())


def test_streight_line():
    _draw_lines(xys(0, 0, 0, 20), 5,
                [("line", (xys(0, 0, 0, 20),), {})])


def test_forward_down():
    _draw_lines(xys(0, 0, 20, 0, 20, 20), 5,
                [("line", (xys(0, 0, 15, 0),), {}),
                 ("arc", ([10, 0, 20, 10], 270, 360), {}),
                 ("line", (xys(20, 5, 20, 20),), {})])


def test_forward_up():
    _draw_lines(xys(0, 0, 20, 0, 20, -20), 5,
                [("line", (xys(0, 0, 15, 0),), {}),
                 ("arc", ([10, -10, 20, 0], 0, 90), {}),
                 ("line", (xys(20, -5, 20, -20),), {})])


def test_backward_down():
    _draw_lines(xys(0, 0, -20, 0, -20, 20), 5,
                [("line", (xys(0, 0, -15, 0),), {}),
                 ("arc", ([-20, 0, -10, 10], 180, 270), {}),
                 ("line", (xys(-20, 5, -20, 20),), {})])


def test_backward_up():
    _draw_lines(xys(0, 0, -20, 0, -20, -20), 5,
                [("line", (xys(0, 0, -15, 0),), {}),
                 ("arc", ([-20, -10, -10, 0], 90, 180), {}),
                 ("line", (xys(-20, -5, -20, -20),), {})])


def test_down_forward():
    _draw_lines(xys(0, 0, 0, 20, 20, 20), 5,
                [("line", (xys(0, 0, 0, 15),), {}),
                 ("arc", ([0, 10, 10, 20], 90, 180), {}),
                 ("line", (xys(5, 20, 20, 20),), {})])


def test_down_backward():
    _draw_lines(xys(0, 0, 0, 20, -20, 20), 5,
                [("line", (xys(0, 0, 0, 15),), {}),
                 ("arc", ([-10, 10, 0, 20], 0, 90), {}),
                 ("line", (xys(-5, 20, -20, 20),), {})])


def test_up_forward():
    _draw_lines(xys(0, 0, 0, -20, 20, -20), 5,
                [("line", (xys(0, 0, 0, -15),), {}),
                 ("arc", ([0, -20, 10, -10], 180, 270), {}),
                 ("line", (xys(5, -20, 20, -20),), {})])


def test_up_backward():
    _draw_lines(xys(0, 0, 0, -20, -20, -20), 5,
                [("line", (xys(0, 0, 0, -15),), {}),
                 ("arc", ([-10, -20, 0, -10], 270, 360), {}),
                 ("line", (xys(-5, -20, -20, -20),), {})])


def test_angled_lines():
    _draw_lines(xys(0, 0, 10, 10, 10, 20), 5,
                [("line", (xys(0, 0, 10, 10),), {}),
                 ("line", (xys(10, 10, 10, 20),), {})])
