# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer


class NoneShape(NodeShape):
    def __init__(self, node, metrix=None):
        super(NoneShape, self).__init__(node, metrix)

        p = metrix.cell(node).center()
        self.connectors = [p, p, p, p]

    def render_label(self, drawer, **kwargs):
        pass

    def render_shape(self, drawer, format, **kwargs):
        pass


def setup(self):
    install_renderer('none', NoneShape)
