# -*- coding: utf-8 -*-


def render_node(drawer, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    font = kwargs.get('font')
    fill = kwargs.get('fill')
    badgeFill = kwargs.get('badgeFill')

    m = metrix.node(node)

    if node.background:
        drawer.rectangle(m.box(), fill=node.color)
        drawer.loadImage(node.background, m.box())
        drawer.rectangle(m.box(), outline=outline, style=node.style)
    else:
        drawer.rectangle(m.box(), outline=outline,
                         fill=node.color, style=node.style)

    drawer.textarea(m.coreBox(), node.label, fill=fill,
                    font=font, fontsize=metrix.fontSize,
                    lineSpacing=metrix.lineSpacing)

    if node.numbered != None:
        xy = m.topLeft()
        r = metrix.cellSize

        box = (xy.x - r, xy.y - r, xy.x + r, xy.y + r)
        drawer.ellipse(box, outline=fill, fill=badgeFill)
        drawer.textarea(box, node.numbered, fill=fill,
                        font=font, fontsize=metrix.fontSize)


def render_shadow(drawer, node, metrix, fill):
    box = metrix.node(node).box()
    shadow = (box[0] + metrix.shadowOffsetX,
              box[1] + metrix.shadowOffsetY,
              box[2] + metrix.shadowOffsetX,
              box[3] + metrix.shadowOffsetY)

    drawer.rectangle(shadow, fill=fill, filter='transp-blur')
