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

import os
import re
import sys
from ConfigParser import SafeConfigParser
from optparse import OptionParser
import blockdiag
import DiagramDraw
import diagparser
from builder import ScreenNodeBuilder
from blockdiag.utils.fontmap import parse_fontpath, FontMap


def parse_option():
    version = "%%prog %s" % blockdiag.__version__
    usage = "usage: %prog [options] infile"
    p = OptionParser(usage=usage, version=version)
    p.add_option('-a', '--antialias', action='store_true',
                 help='Pass diagram image to anti-alias filter')
    p.add_option('-c', '--config',
                 help='read configurations from FILE', metavar='FILE')
    p.add_option('-o', dest='filename',
                 help='write diagram to FILE', metavar='FILE')
    p.add_option('-f', '--font', default=[], action='append',
                 help='use FONT to draw diagram', metavar='FONT')
    p.add_option('--fontmap',
                 help='use FONTMAP file to draw diagram', metavar='FONT')
    p.add_option('-s', '--separate', action='store_true',
                 help='Separate diagram images for each group (SVG only)')
    p.add_option('-T', dest='type', default='PNG',
                 help='Output diagram as TYPE format')
    p.add_option('--nodoctype', action='store_true',
                 help='Do not output doctype definition tags (SVG only)')
    options, args = p.parse_args()

    if len(args) == 0:
        p.print_help()
        sys.exit(0)

    options.type = options.type.upper()
    if not options.type in ('SVG', 'PNG', 'PDF'):
        msg = "unknown format: %s" % options.type
        raise RuntimeError(msg)

    if options.type == 'PDF':
        try:
            import reportlab.pdfgen.canvas
        except ImportError:
            msg = "could not output PDF format; Install reportlab."
            raise RuntimeError(msg)

    if options.nodoctype and options.type != 'SVG':
        msg = "--nodoctype option work in SVG images."
        raise RuntimeError(msg)

    if options.config and not os.path.isfile(options.config):
        msg = "config file is not found: %s" % options.config
        raise RuntimeError(msg)

    configpath = options.config or "%s/.blockdiagrc" % os.environ.get('HOME')
    if os.path.isfile(configpath):
        config = SafeConfigParser()
        config.read(configpath)

        if config.has_option('blockdiag', 'fontpath'):
            fontpath = config.get('blockdiag', 'fontpath')
            options.font.append(fontpath)

        if config.has_option('blockdiag', 'fontmap'):
            if options.fontmap is None:
                fontmap = config.get('blockdiag', 'fontmap')

        if options.fontmap is None:
            options.fontmap = configpath

    if options.fontmap and not os.path.isfile(options.fontmap):
        msg = "fontmap file is not found: %s" % options.fontmap
        raise RuntimeError(msg)

    return options, args


def detectfont(options):
    fonts = ['c:/windows/fonts/VL-Gothic-Regular.ttf',  # for Windows
             'c:/windows/fonts/msmincho.ttf',  # for Windows
             '/usr/share/fonts/truetype/ipafont/ipagp.ttf',  # for Debian
             '/usr/local/share/font-ipa/ipagp.otf',  # for FreeBSD
             '/Library/Fonts/Hiragino Sans GB W3.otf',  # for MacOS
             '/System/Library/Fonts/AppleGothic.ttf']  # for MacOS

    fontpath = None
    if options.font:
        for path in options.font:
            _path, index = parse_fontpath(path)
            if os.path.isfile(_path):
                fontpath = path
                break
        else:
            msg = 'fontfile is not found: %s' % options.font
            raise RuntimeError(msg)

    if fontpath is None:
        for path in fonts:
            _path, index = parse_fontpath(path)
            if os.path.isfile(_path):
                fontpath = path
                break

    return fontpath


def create_fontmap(options):
    fontmap = FontMap(options.fontmap)
    if fontmap.find().path is None or options.font:
        fontpath = detectfont(options)
        fontmap.set_default_font(fontpath)

    return fontmap


def main():
    try:
        options, args = parse_option()
    except RuntimeError, e:
        sys.stderr.write("ERROR: %s\n" % e)
        return

    infile = args[0]
    if options.filename:
        outfile = options.filename
    elif infile == '-':
        outfile = 'output.' + options.type.lower()
    else:
        outfile = re.sub('\..*', '', infile) + '.' + options.type.lower()

    try:
        if infile == '-':
            import codecs
            stream = codecs.getreader('utf-8')(sys.stdin)
            tree = diagparser.parse_string(stream.read())
        else:
            tree = diagparser.parse_file(infile)

        fontmap = create_fontmap(options)
        if options.separate:
            from builder import SeparateDiagramBuilder

            for i, group in enumerate(SeparateDiagramBuilder.build(tree)):
                outfile2 = re.sub('.svg$', '', outfile) + ('_%d.svg' % (i + 1))
                draw = DiagramDraw.DiagramDraw(options.type, group, outfile2,
                                               fontmap=fontmap,
                                               antialias=options.antialias,
                                               nodoctype=options.nodoctype)
                draw.draw()
                draw.save()
        else:
            diagram = ScreenNodeBuilder.build(tree)

            draw = DiagramDraw.DiagramDraw(options.type, diagram, outfile,
                                           fontmap=fontmap,
                                           antialias=options.antialias,
                                           nodoctype=options.nodoctype)
            draw.draw()
            draw.save()
    except UnicodeEncodeError, e:
        msg = "ERROR: UnicodeEncodeError caught (check your font settings)\n"
        sys.stderr.write(msg)
    except Exception, e:
        sys.stderr.write("ERROR: %s\n" % e)
