# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils import Box, XY


class MiniDiamond(NodeShape):
    def __init__(self, node, metrics=None):
        super(MiniDiamond, self).__init__(node, metrics)

        r = metrics.cellsize
        m = metrics.cell(node)
        c = m.center
        self.connectors = (XY(c.x, c.y - r),
                           XY(c.x + r, c.y),
                           XY(c.x, c.y + r),
                           XY(c.x - r, c.y),
                           XY(c.x, c.y - r))
        self.textbox = Box(m.top.x, m.top.y, m.right.x, m.right.y)
        self.textalign = 'left'

    def render_shape(self, drawer, format, **kwargs):
        fill = kwargs.get('fill')

        # draw outline
        if kwargs.get('shadow'):
            diamond = self.shift_shadow(self.connectors)
            drawer.polygon(diamond, fill=fill, outline=fill,
                             filter='transp-blur')
        else:
            drawer.polygon(self.connectors, fill=self.node.color,
                           outline=self.node.linecolor, style=self.node.style)


def setup(self):
    install_renderer('minidiamond', MiniDiamond)
