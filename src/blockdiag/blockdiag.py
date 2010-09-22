#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import sys
import re
import uuid
from optparse import OptionParser
import Image
import ImageFont
import DiagramDraw
import diagparser
from DiagramDraw import XY


class ScreenNode:
    @classmethod
    def getId(klass, node):
        try:
            node_id = node.id
        except AttributeError:
            node_id = node

        return node_id

    def __init__(self, id):
        self.id = id
        if id:
            self.label = re.sub('^"?(.*?)"?$', '\\1', id)
        else:
            self.label = ''
        self.xy = XY(0, 0)
        self.color = None
        self.group = None
        self.width = 1
        self.height = 1
        self.drawable = 1

    def copyAttributes(self, other):
        self.label = other.label
        self.xy = other.xy
        self.color = other.color

    def setAttributes(self, attrs):
        for attr in attrs:
            value = re.sub('^"?(.*?)"?$', '\\1', attr.value)
            if attr.name == 'label':
                self.label = value
            elif attr.name == 'color':
                self.color = value
            else:
                msg = "Unknown node attribute: %s.%s" % (self.id, attr.name)
                raise AttributeError(msg)


class ScreenEdge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.group = None
        self.color = None
        self.noweight = None
        self.dir = 'forward'

    def copyAttributes(self, other):
        self.color = other.color
        self.noweight = other.noweight
        self.dir = other.dir

    def setAttributes(self, attrs):
        for attr in attrs:
            value = re.sub('^"?(.*?)"?$', '\\1', attr.value)
            if attr.name == 'color':
                self.color = value
            elif attr.name == 'dir':
                dir = value.lower()
                if dir in ('back', 'both', 'none'):
                    self.dir = dir
                else:
                    self.dir = 'forward'
            elif attr.name == 'noweight':
                if value.lower() == 'none':
                    self.noweight = None
                else:
                    self.noweight = 1
            else:
                raise AttributeError("Unknown edge attribute: %s" % attr.name)


class ScreenGroup(ScreenNode):
    def __init__(self, id):
        ScreenNode.__init__(self, id)
        self.label = ''
        self.nodes = []
        self.edges = []
        self.width = 1
        self.height = 1
        self.drawable = 0


class ScreenNodeBuilder:
    @classmethod
    def build(klass, tree):
        return klass()._build(tree)

    def __init__(self):
        self.uniqNodes = {}
        self.nodeOrder = []
        self.uniqLinks = {}
        self.widthRefs = []
        self.heightRefs = []
        self.rows = 0

    def _build(self, tree):
        self.buildNodeList(tree)

        return (self.uniqNodes.values(), self.uniqLinks.values())

    def getScreenNode(self, id):
        if id in self.uniqNodes:
            node = self.uniqNodes[id]
        else:
            node = ScreenNode(id)
            self.uniqNodes[id] = node
            self.nodeOrder.append(node)

        return node

    def getScreenGroup(self, id):
        if id is None:
            # generate new id
            id = 'ScreenGroup_%s' % uuid.uuid1()

        if id in self.uniqNodes:
            group = self.uniqNodes[id]
        else:
            group = ScreenGroup(id)
            self.uniqNodes[id] = group
            self.nodeOrder.append(group)

        return group

    def getScreenEdge(self, id1, id2):
        link = (self.getScreenNode(id1), self.getScreenNode(id2))

        if link in self.uniqLinks:
            edge = self.uniqLinks[link]
        else:
            edge = ScreenEdge(link[0], link[1])
            self.uniqLinks[link] = edge

        return edge

    def getChildren(self, node):
        node_id = ScreenNode.getId(node)

        uniq = {}
        for edge in self.uniqLinks.values():
            if edge.noweight == None:
                if node_id == None:
                    uniq[edge.node1] = 1
                elif edge.node1.id == node_id:
                    uniq[edge.node2] = 1
                elif edge.node1.group and edge.node1.group.id == node_id:
                    uniq[edge.node2] = 1

        children = []
        for node in uniq.keys():
            if node.group:
                children.append(node.group)
            else:
                children.append(node)

        order = self.nodeOrder
        children.sort(lambda x, y: cmp(order.index(x), order.index(y)))

        return children

    def isCircularRef(self, node1, node2):
        node1_id = ScreenNode.getId(node1)

        referenced = False
        children = [node2]
        uniqNodes = {}
        for child in children:
            if node1_id == child.id:
                referenced = True
                break

            for node in self.getChildren(child):
                if not node in uniqNodes:
                    children.append(node)
                    uniqNodes[node] = 1

        return referenced

    def setNodeWidth(self, node=None):
        node_id = ScreenNode.getId(node)

        self.widthRefs.append(node_id)
        for child in self.getChildren(node_id):
            is_ref = child.id in self.widthRefs

            if is_ref and self.isCircularRef(node_id, child):
                pass
            elif child.group:
                pass
            elif is_ref and node_id == None:
                pass
            else:
                if node_id == None:
                    child.xy = XY(0, child.xy.y)
                elif node.xy.x + 1 > child.xy.x:
                    child.xy = XY(node.xy.x + node.width, child.xy.y)
                self.setNodeWidth(child)

    def setNodeHeight(self, node, baseHeight):
        node.xy = XY(node.xy.x, baseHeight)
        self.heightRefs.append(node.id)

        height = 0
        for child in self.getChildren(node):
            if child.id in self.heightRefs:
                pass
            elif node.xy.x < child.xy.y:
                pass
            else:
                height += self.setNodeHeight(child, baseHeight + height)

        if height < node.height:
            height = node.height

        return height

    def buildNodeList(self, tree):
        for stmt in tree.stmts:
            if isinstance(stmt, diagparser.Node):
                node = self.getScreenNode(stmt.id)
                node.setAttributes(stmt.attrs)
            elif isinstance(stmt, diagparser.Edge):
                while len(stmt.nodes) >= 2:
                    edge = self.getScreenEdge(stmt.nodes.pop(0), stmt.nodes[0])
                    edge.setAttributes(stmt.attrs)
            elif isinstance(stmt, diagparser.SubGraph):
                nodes, edges = ScreenNodeBuilder.build(stmt)
                group = self.getScreenGroup(stmt.id)
                group.width = max(x.xy.x for x in nodes) + 1
                group.height = max(x.xy.y for x in nodes) + 1

                for node in nodes:
                    o = self.getScreenNode(node.id)
                    if o.group:
                        msg = "ScreenNode could not belong to two groups"
                        raise RuntimeError(msg)
                    o.copyAttributes(node)
                    o.group = group

                    group.nodes.append(o)

                for edge in edges:
                    o = self.getScreenEdge(edge.node1.id, edge.node2.id)
                    o.copyAttributes(edge)
                    o.group = group

                    group.edges.append(o)
            else:
                raise AttributeError("Unknown sentense: " + str(type(stmt)))

        self.setNodeWidth()

        height = 0
        toplevel_nodes = [x for x in self.nodeOrder if x.xy.x == 0]
        for node in toplevel_nodes:
            if not node.group:
                height += self.setNodeHeight(node, height)

        for node in self.nodeOrder:
            if isinstance(node, ScreenGroup):
                for child in node.nodes:
                    child.xy = (node.xy.x + child.xy.x, node.xy.y + child.xy.y)


def main():
    usage = "usage: %prog [options] infile"
    p = OptionParser(usage=usage)
    p.add_option('-o', dest='filename',
                 help='write diagram to FILE', metavar='FILE')
    p.add_option('-f', '--font', dest='font',
                 help='use FONT to draw diagram', metavar='FONT')
    (options, args) = p.parse_args()

    if len(args) == 0:
        p.print_help()
        exit(0)

    fonts = [options.font,
             'c:/windows/fonts/VL-Gothic-Regular.ttf',
             'c:/windows/fonts/msmincho.ttf',
             '/usr/share/fonts/truetype/ipafont/ipagp.ttf']

    ttfont = None
    for path in fonts:
        if path and os.path.isfile(path):
            ttfont = ImageFont.truetype(path, 11)
            break

    draw = DiagramDraw.DiagramDraw()

    infile = args[0]
    if options.filename:
        outfile = options.filename
    else:
        outfile = re.sub('\..*', '', infile) + '.png'

    try:
        tree = diagparser.parse_file(infile)
        nodelist, edgelist = ScreenNodeBuilder.build(tree)

        draw.screennodelist(nodelist, font=ttfont)
        draw.edgelist(edgelist)
    except Exception, e:
        import traceback
        traceback.print_exc()

        name = e.__class__.__name__
        print "[%s] %s" % (name, e)
        exit(1)

    draw.save(outfile, 'PNG')


if __name__ == '__main__':
    main()