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


class Box(NodeShape):
    def render_shape(self, drawer, format, **kwargs):
        fill = kwargs.get('fill')

        # draw outline
        box = self.metrics.cell(self.node).box
        if kwargs.get('shadow'):
            box = self.shift_shadow(box)
            if kwargs.get('style') == 'blur':
                drawer.rectangle(box, fill=fill, outline=fill,
                                 filter='transp-blur')
            else:
                drawer.rectangle(box, fill=fill, outline=fill)
        elif self.node.background:
            drawer.rectangle(box, fill=self.node.color,
                             outline=self.node.color)
            drawer.image(self.textbox, self.node.background)
            drawer.rectangle(box, outline=self.node.linecolor,
                             style=self.node.style)
        else:
            drawer.rectangle(box, fill=self.node.color,
                             outline=self.node.linecolor,
                             style=self.node.style)


def setup(self):
    install_renderer('box', Box)
