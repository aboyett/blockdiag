# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os
import re
from blockdiag.builder import ScreenNodeBuilder
from blockdiag.parser import parse_file, parse_string

try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO


def supported_pil():
    try:
        import _imagingft
        _imagingft

        return True
    except:
        return False


def with_pil(fn):
    if not supported_pil():
        fn.__test__ = False

    return fn


def supported_pdf():
    try:
        import reportlab
        reportlab

        return True
    except:
        return False


def with_pdf(fn):
    if not supported_pdf():
        fn.__test__ = False

    return fn


def argv_wrapper(func, argv=[]):
    def wrap(*args, **kwargs):
        try:
            argv = sys.argv
            sys.argv = []
            func(*args, **kwargs)
        finally:
            sys.argv = argv

    wrap.__name__ = func.__name__
    return wrap


def stderr_wrapper(func):
    def wrap(*args, **kwargs):
        try:
            stderr = sys.stderr
            sys.stderr = StringIO()

            print(args, kwargs)
            func(*args, **kwargs)
        finally:
            if sys.stderr.getvalue():
                print("---[ stderr ] ---")
                print(sys.stderr.getvalue())

            sys.stderr = stderr

    wrap.__name__ = func.__name__
    return wrap


class BuilderTestCase(unittest.TestCase):
    def build(self, filename):
        basedir = os.path.dirname(__file__)
        pathname = os.path.join(basedir, 'diagrams', filename)
        return ScreenNodeBuilder.build(parse_file(pathname))

    def __getattr__(self, name):
        if name.startswith('assertNode'):
            def asserter(diagram, attributes):
                attr_name = name.replace('assertNode', '').lower()
                print("[node.%s]" % attr_name)
                for node in (n for n in diagram.nodes if n.drawable):
                    print(node)
                    excepted = attributes[node.id]
                    self.assertEqual(excepted, getattr(node, attr_name))

            return asserter
        elif name.startswith('assertEdge'):
            def asserter(diagram, attributes):
                attr_name = name.replace('assertEdge', '').lower()
                print("[edge.%s]" % attr_name)
                for edge in diagram.edges:
                    print(edge)
                    expected = attributes[(edge.node1.id, edge.node2.id)]
                    self.assertEqual(expected, getattr(edge, attr_name))

            return asserter
        else:
            return getattr(super(BuilderTestCase, self), name)
