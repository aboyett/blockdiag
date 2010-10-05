#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import Image
import ImageDraw
import ImageFont
import ImageFilter
from utils.XY import XY


class TextFolder:
    def __init__(self, box, string, **kwargs):
        font = kwargs.get('font')
        if font:
            fontsize = kwargs.get('fontsize', 11)
            self.ttfont = ImageFont.truetype(font, fontsize)
            self.scale = 1
        else:
            self.ttfont = None
            self.scale = kwargs.get('scale', 1)

        self.box = box
        self.string = string
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.image = Image.new('1', (1, 1))
        self.draw = ImageDraw.Draw(self.image)

        self._result = self._lines()

    def textsize(self, string):
        return self.draw.textsize(string, font=self.ttfont)

    def height(self):
        height = 0
        for string in self._result:
            height += self.textsize(string)[1]

        if len(self._result) > 1:
            height += (len(self._result) - 1) * self.lineSpacing

        return height

    def each_line(self):
        size = XY(self.box[2] - self.box[0], self.box[3] - self.box[1])

        height = int(math.ceil((size.y - self.height()) / 2.0))
        base_xy = XY(self.box[0], self.box[1])

        for string in self._result:
            textsize = self.textsize(string)
            halign = size.x - textsize[0] * self.scale

            x = int(math.ceil(halign / 2.0))
            draw_xy = XY(base_xy.x + x, base_xy.y + height)

            yield string, draw_xy

            height += textsize[1] + self.lineSpacing

    def _lines(self):
        lines = []
        size = (self.box[2] - self.box[0], self.box[3] - self.box[1])

        height = 0
        truncated = 0
        for line in self.string.splitlines():
            while line:
                string = line.strip()
                for i in range(0, len(string)):
                    length = len(string) - i
                    metrics = self.textsize(string[0:length])

                    if metrics[0] <= size[0]:
                        break

                if size[1] < height + metrics[1]:
                    truncated = 1
                    break

                lines.append(string[0:length])
                line = string[length:]

                height += metrics[1] + self.lineSpacing

        # truncate last line.
        if truncated:
            string = lines.pop()
            for i in range(0, len(string)):
                if i == 0:
                    truncated = string + ' ...'
                else:
                    truncated = string[0:-i] + ' ...'

                metrics = self.textsize(truncated)
                if metrics[0] <= size[0]:
                    lines.append(truncated)
                    break

        return lines


class ImageDrawEx(ImageDraw.ImageDraw):
    def __init__(self, im, scale_ratio, mode=None):
        self.image = im
        self.scale_ratio = scale_ratio
        self.mode = mode
        ImageDraw.ImageDraw.__init__(self, im, mode)

    def rectangle(self, box, **kwargs):
        thick = kwargs.get('width', self.scale_ratio)
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')

        if thick == 1:
            ImageDraw.ImageDraw.rectangle(self, box, **kwargs)
        else:
            d = math.ceil(thick / 2.0)

            ImageDraw.ImageDraw.rectangle(self, box, **kwargs)

            x1, y1, x2, y2 = box
            self.line(((x1, y1 - d), (x1, y2 + d)), fill=outline, width=thick)
            self.line(((x2, y1 - d), (x2, y2 + d)), fill=outline, width=thick)
            self.line(((x1, y1), (x2, y1)), fill=outline, width=thick)
            self.line(((x1, y2), (x2, y2)), fill=outline, width=thick)

    def setupFont(self, font, fontsize):
        if font:
            ttfont = ImageFont.truetype(font, fontsize)
        else:
            ttfont = None

        return ttfont

    def truetypeText(self, xy, string, **kwargs):
        fill = kwargs.get('fill')
        font = kwargs.get('font')
        fontsize = kwargs.get('fontsize', 11)
        ttfont = self.setupFont(font, fontsize)

        if ttfont is None:
            if self.scale_ratio == 1:
                ImageDraw.ImageDraw.text(self, xy, string, fill=fill)
            else:
                size = self.textsize(string)
                image = Image.new('RGBA', size)
                draw = ImageDraw.Draw(image)
                draw.text((0, 0), string, fill=fill)
                del draw

                basesize = (size[0] * self.scale_ratio,
                            size[1] * self.scale_ratio)
                text_image = image.resize(basesize, Image.ANTIALIAS)

                self.image.paste(text_image, xy, text_image)
        else:
            size = self.textsize(string, font=ttfont)

            # Generate mask to support BDF(bitmap font)
            mask = Image.new('1', size)
            draw = ImageDraw.Draw(mask)
            draw.text((0, 0), string, fill='white', font=ttfont)

            # Rendering text
            filler = Image.new('RGB', size, fill)
            self.image.paste(filler, xy, mask)

            ImageDraw.ImageDraw.__init__(self, self.image, self.mode)

    def text(self, box, string, **kwargs):
        lines = TextFolder(box, string, scale=self.scale_ratio, **kwargs)
        for string, xy in lines.each_line():
            self.truetypeText(xy, string, **kwargs)

    def loadImage(self, filename, box):
        box_width = box[2] - box[0]
        box_height = box[3] - box[1]

        # resize image.
        image = Image.open(filename)
        w = min([box_width, image.size[0] * self.scale_ratio])
        h = min([box_height, image.size[1] * self.scale_ratio])
        image.thumbnail((w, h), Image.ANTIALIAS)

        # centering image.
        w, h = image.size
        if box_width > w:
            x = box[0] + (box_width - w) / 2
        else:
            x = box[0]

        if box_height > h:
            y = box[1] + (box_height - h) / 2
        else:
            y = box[1]

        self.image.paste(image, (x, y))
        ImageDraw.ImageDraw.__init__(self, self.image, self.mode)
