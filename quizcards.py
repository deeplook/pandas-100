#!/usr/bin/env python

"""
This generates double-sided quiz cards based on a MarkDown file.

Dependencies:

    - pip install reportlab
    - DejaVuSansCondensed.ttf (if present else Helvetica)
    - DejaVuSansCondensed-Bold.ttf (if present else Helvetica-Bold)
    - nk57-monospace-cd-sb.ttf (if present else Courier)

Usage:

    python3 quizcards.py "100 pandas exercises.md"
"""

import re
import io
import sys
import copy
import os.path
import argparse

from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.pagesizes import A3, A4, A5, A6, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pygments2xpre import pygments2xpre
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, XPreformatted
from reportlab.platypus.flowables import Image, Spacer, KeepInFrame


# Text Styling 

def register_fonts():
    "Register optional fonts for better rendering."

    registered_fonts = {
        'DejaVu-Sans-Condensed': {
            'default': 'Helvetica',
            'registered': False,
            'path': 'DejaVuSansCondensed.ttf',
            'link': 'https://github.com/dejavu-fonts/dejavu-fonts'},
        'DejaVu-Sans-Condensed-Bold': {
            'default': 'Helvetica-Bold',
            'registered': False,
            'path': 'DejaVuSansCondensed-Bold.ttf',
            'link': 'https://github.com/dejavu-fonts/dejavu-fonts'},
        'Monospace-Condensed-Semibold': {
            'default': 'Courier',
            'registered': False,
            'path': 'nk57-monospace-cd-sb.ttf',
            'link': 'http://www.dafont.com/nk57-monospace.font'},
    }
    for name in registered_fonts:
        f = registered_fonts
        default, path, link = f[name]['default'], f[name]['path'], f[name]['link']
        if os.path.exists(path):
            font = TTFont(name, path)
            pdfmetrics.registerFont(font)
            registered_fonts[name]['registered'] = True
        else:
            print('Font %s not found, using %s.' % (name, default))
            print('See %s' % link)
    return registered_fonts


rf = register_fonts()

styleSheet = getSampleStyleSheet()

h1 = styleSheet['Title']
name = 'DejaVu-Sans-Condensed-Bold'
h1.fontName = name if rf[name]['registered'] else rf[name]['default']

bt = styleSheet['BodyText']
name = 'DejaVu-Sans-Condensed'
bt.fontName = name if rf[name]['registered'] else rf[name]['default']
bt.fontSize = 14
bt.leading = bt.fontSize * 1.25

fine = copy.deepcopy(bt)
fine.fontSize = 10
fine.leading = fine.fontSize * 1.25

code = styleSheet['Code']
name = 'Monospace-Condensed-Semibold'
code.fontName = name if rf[name]['registered'] else rf[name]['default']
code.leftIndent = 0
code.fontSize = 10
code.leading = fine.fontSize * 1.25


# Utils

def reverse_seq(seq):
    "Return reversed sequence, being either a list, tuple or string."

    seqList = [el for el in seq]
    seqList.reverse()

    if type(seq) is tuple:
        res = tuple(seqList)
    elif type(seq) is str:
        res = "".join(seqList)
    else:
        res = seqList

    return res


class Record(object):
    def __init__(self, **kwdict):
        for k, v in kwdict.items():
            setattr(self, k, v)


# Core stuff

class Card(object):
    "A mini-page like card."

    lm, rm = 3 * mm, 3 * mm  # left/right margin
    tm, bm = 3 * mm, 3 * mm  # top/bottom margin
    fn, fs = bt, 10

    def __init__(self, frame=False, debug=False, **dikt):
        # set received vars as instance variables
        self.frame = frame
        self.debug = debug
        for k, v in dikt.items():
            setattr(self, k, v)

    def render(self, **dikt):
        for k, v in dikt.items():
            setattr(self, k, v)

        # set derived instance variables
        self.width, self.height = self.size
        self.xp = self.x0 + self.lm
        self.yp = self.y0 + self.height - self.tm

        # start drawing
        self.begin()
        self.draw()
        self.end()

    def begin(self):
        canv = self.canv
        canv.setStrokeColor(colors.black)
        canv.setFillColor(colors.black)
        canv.setLineWidth(0.25 * mm)
        canv.setLineCap(1)

    def addSpace(self, x=0, y=0):
        "Add empty space."

        self.xp += x
        self.yp += y

    def drawFrame(self):
        if self.frame:
            c = self.canv
            c.saveState()
            c.setStrokeColor(colors.lightgrey)
            c.setLineWidth(0.25 * mm)
            c.rect(self.x0, self.y0, self.width, self.height)
            c.setStrokeColor(colors.black)
            c.restoreState()

    def end(self):
        if self.frame:
            self.drawFrame()

    def draw(self):
        pass


class QuizCard(Card):
    "Quiz card with a question and answer on two sides."

    def resize_images(self, story):
        # replace images with resized ones fitting into the available width
        W, H = (
            self.width - self.lm - self.rm), self.height - self.tm - self.bm
        for i, el in enumerate(story):
            if el.__class__ == Image:
                img = PIL.Image.open(el.filename)
                h = W / img.size[0] * img.size[1]
                img = Image(el.filename, width=w, height=h, kind='direct',
                            mask="auto", lazy=1)
                story[i] = img
            elif type(el) == str:
                story[i] = Paragraph(el, bt)  # Spacer(0, 0)

    def fits(self, flowables):
        story = flowables
        self.resize_images(story)

        W, H = (
            self.width - self.lm - self.rm), self.height - self.tm - self.bm
        canv = Canvas(io.StringIO(), (W, H))
        total_height = sum([el.wrapOn(canv, W, 0)[1] + bt.spaceBefore
                            for el in story])
        if getattr(self, "verbose", False) == True:
            print("***", total_height / mm, H / mm, \
                [txt.text[:5] for txt in story])
        return total_height < H

    def draw(self):
        self.canv.saveState()

        XP, YP = self.xp, self.yp
        self.resize_images(self.text)
        story = self.text
        W, H = (self.width - self.lm - self.rm), self.yp - self.y0 - self.bm
        # possible modes: shrink, truncate, overflow, error
        frame = KeepInFrame(W, H, story, mode="shrink")
        w, h = frame.wrapOn(self.canv, W, H)
        frame.drawOn(self.canv, self.xp, self.yp - h)
        self.addSpace(0, -h - 5 * mm)
        self.canv.restoreState()


# Layouting

def maximize_cards_on_page(cardSize, pageSize, margins=None, autoRotate=False):
    "Maximize number of cards on a page, perhaps turning page 90 degrees."

    if margins is None:
        margins = Record(lm=0, rm=0, tm=0, bm=0)

    f1 = (pageSize[0] - margins.lm - margins.rm) / cardSize[0]
    f2 = (pageSize[1] - margins.bm - margins.tm) / cardSize[1]
    i1, i2 = int(f1), int(f2)
    n1 = i1 * i2

    g1 = (pageSize[0] - margins.lm - margins.rm) / cardSize[1]
    g2 = (pageSize[1] - margins.bm - margins.tm) / cardSize[0]
    j1, j2 = int(g1), int(g2)
    m1 = j1 * j2

    if autoRotate and m1 > n1:
        i1, i2 = j1, j2
        pageSize = reverse_seq(pageSize)
        i1, i2 = i2, i1

    if autoRotate and pageSize[0] <= pageSize[1]:
        if cardSize[0] > cardSize[1]:
            i1, i2 = i2, i1

    newPageSize = pageSize
    numCardsX, numCardsY = i1, i2

    return newPageSize, numCardsX, numCardsY


def add_size_info_label(canv, x, y, pageSize, cardSize):
    "Put info label about used sizes on a page."

    canv.setFont(bt.fontName, 8)
    args = (pageSize + cardSize)
    args = tuple([a / mm for a in args])
    desc = "paper: %3.0f x %3.0f mm, cards: %3.0f x %3.0f mm" % args
    canv.drawString(x, y + cardSize[1] + 6, desc)


def layout(path, cards, pageSize, cardSize,
           autoRotate=True, frame=False, debug=False):
    "Make double-sided multi card sheet with all different cards per sheet."

    nppm = Record(lm=7.21 * mm, rm=7.21 * mm, tm=15.1 * mm, bm=15.1 * mm)
    pageSize, i1, i2 = maximize_cards_on_page(
        cardSize, pageSize, margins=nppm, autoRotate=autoRotate)

    canv = Canvas(path, pagesize=pageSize)
    xc, yc = pageSize[0] / 2.0, pageSize[1] / 2.0
    cw, ch = cardSize

    # regroup pages for double-sided printing
    cardGroups = []
    k = 0
    for j, card in enumerate(cards):
        if j > 0 and j % (2 * i1 * i2) == 0:
            cardGroups.append(cards[k:j:2])
            cardGroups.append(cards[k + 1:j + 1:2])
            k = j
    cardGroups.append(cards[k::2])
    cardGroups.append(cards[k + 1::2])

    # place cards on paper
    for g, cardGroup in enumerate(cardGroups):
        x0, y0 = xc - i1 * cw / 2., yc - i2 * ch / 2.
        r = range
        if g % 2 == 0:
            coords = [(x0 + x * cw, y0 + y * ch)
                      for y in reverse_seq(r(i2)) for x in r(i1)]
        else:
            coords = [(x0 + x * cw, y0 + y * ch)
                      for y in reverse_seq(r(i2)) for x in reverse_seq(r(i1))]
        j = 0
        while j < len(cardGroup):
            obj = cardGroup[j]
            if g % 2 != 0:
                if hasattr(obj, "lm"):
                    obj.rm = obj.lm
                    delattr(obj, "lm")
            x, y = coords[j % (i1 * i2)]
            if j % (i1 * i2) == 0:
                add_size_info_label(canv, x, y, pageSize, cardSize)
            obj.render(canv=canv, x0=x, y0=y, size=cardSize,
                       frame=frame, debug=debug)
            j += 1
        if frame:
            canv.rect(0, 0, pageSize[0], pageSize[1])
        canv.showPage()

    canv.save()



def extract_markdown(path):
    "Read a MarkDown file and return a cover and list of Q/A tuples."

    content = open(path).read()

    # find cover content (only title and list of paragraphs)
    m_title = re.search('# +(.*)', content)
    title = m_title.groups()[0]
    m_q1 = re.search('#### +(.*)', content)
    paras = content[m_title.end():m_q1.start()].strip().split('\n')
    repl = lambda m: '<a href="%s" color="blue">%s</a>' % (m.groups()[0], m.groups()[0])
    paras = [p for p in paras if p]
    paras = [re.sub('\<(.*?)\>', repl, p) for p in paras]
    cover = (title, paras)

    # remove MarkDown escapes
    for ch in "[]*":
        content = content.replace('\\' + ch, ch)

    # replace stars if using Helvetica (not needed for DejaVu-Sans)
    if bt.fontName.startswith('Helvetica'):
        content = re.sub('(★+☆*)', lambda m: '*'*m.group().count('★'), content)

    # build question/aswer tuples
    q_pat = '#### +(\d+\. +.*)'
    q_s = re.findall(q_pat, content)
    a_pat = "```\s*python\s*\n(.*?)```"
    a_s = re.findall(a_pat, content, re.S)
    qa = zip(q_s, a_s)

    return cover, qa


def markdown_to_platypus(path):
    "Convert a specific MarkDown file into ReportLab Platypus items."

    cover, qa = extract_markdown(path)
    title, paras = cover
    cover = [Paragraph(title, h1)] + [Paragraph(p, bt) for p in paras]
    items = [{"q": Paragraph(q, bt), 
              "a": XPreformatted(pygments2xpre(a), code)} for q, a in qa]
    return cover, items


def make_cards_platypus(cardSize, cover, items, verbose=False):
    "Generate q/a sides of quiz cards from a list of quiz items."

    # cover and items are Platypus flowables!

    cw, ch = cardSize
    kwDict = {
        "lm": 4 * mm, 
        "rm": 4 * mm, 
        "text": "", 
        "width": cw, 
        "height": ch, 
        "verbose": verbose
    }
    q_side = QuizCard(**kwDict)
    a_side = QuizCard(**kwDict)

    # first cover card
    questions = cover
    answers = []

    # rest of the normal cards    
    for i, item in enumerate(items):
        q, a = item["q"], item["a"]
        q_side.text = questions
        a_side.text = answers
        yield q_side, a_side
        questions = [Paragraph("Question:", fine)] + [q]
        answers = [Paragraph("Answer %d:<br/><br/>" % (i + 1), fine)] + [a]
        q_side = QuizCard(**kwDict)
        a_side = QuizCard(**kwDict)

    q_side.text = questions
    a_side.text = answers
    yield q_side, a_side


def make_cards_file(path, cover, items, verbose=False):
    "Make cards with as many items as possible, shrinking too big ones."
    
    cardSize = (9.1 * cm, 5.9 * cm)
    cards = []
    for q, a in make_cards_platypus(cardSize, cover, items, verbose=verbose):
        cards += [q, a]
    
    outPath = os.path.splitext(path)[0] + ".pdf"
    pageSize = landscape(A4)
    layout(outPath, cards, pageSize, cardSize, frame=True, debug=False)

    if verbose:
        print("wrote %s" % outPath)


def _main():
    desc = "Generate quiz cards from dedicated file in MarkDown format."
    parser = argparse.ArgumentParser(description=desc)
    paa = parser.add_argument
    paa("-V", "--verbose",
        action="store_true",
        help="Set verbose output.", 
        dest="verbose")
    paa("paths",
        metavar='PATH',
        help="Path of a MardDown file.",
        nargs='+')

    options = parser.parse_args()
    for path in options.paths:
        if path.lower().endswith(".md"):
            cover, items = markdown_to_platypus(path)
            make_cards_file(path, cover, items, verbose=options.verbose)


if __name__ == "__main__":
    _main()
