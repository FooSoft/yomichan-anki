# -*- coding: utf-8 -*-

# Copyright (C) 2011  Alex Yatskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re
from PyQt4 import QtGui
from util import buildResPath


class Definition:
    def __init__(self, expression, reading, glossary, conjugations, source, sentence):
        self.expression = expression
        self.reading = reading
        self.glossary = glossary
        self.conjugations = conjugations
        self.source = source
        self.sentence = sentence


def decodeContent(content):
    encodings = ['utf-8', 'shift_jis', 'utf-16']
    errors = dict()

    for encoding in encodings:
        try:
            return content.decode(encoding), encoding
        except UnicodeDecodeError, e:
            errors[encoding] = e[2]

    encoding = sorted(errors, key=errors.get, reverse=True)[0]
    return content.decode(encoding, 'replace'), encoding


def stripContentReadings(content):
    return re.sub(u'《[^》]+》', unicode(), content)


def findSentence(content, position):
    quotesFwd = {u'「': u'」', u'『': u'』', u"'": u"'", u'"': u'"'}
    quotesBwd = {u'」': u'「', u'』': u'『', u"'": u"'", u'"': u'"'}
    terminators = u'。．.？?！!'

    quoteStack = list()

    start = 0
    for i in xrange(position, start, -1):
        c = content[i]

        if not quoteStack and (c in terminators or c in quotesFwd or c == '\n'):
            start = i + 1
            break

        if quoteStack and c == quoteStack[0]:
            quoteStack.pop()
        elif c in quotesBwd:
            quoteStack.insert(0, quotesBwd[c])

    quoteStack = list()

    end = len(content)
    for i in xrange(position, end):
        c = content[i]

        if not quoteStack:
            if c in terminators:
                end = i + 1
                break
            elif c in quotesBwd:
                end = i
                break

        if quoteStack and c == quoteStack[0]:
            quoteStack.pop()
        elif c in quotesFwd:
            quoteStack.insert(0, quotesFwd[c])

    return content[start:end].strip()


def replaceMarkupInField(field, markup):
    for marker, value in markup.items():
        field = field.replace(marker, value or unicode())

    return field


def replaceMarkupInFields(fields, markup):
    result = dict()
    for field, value in fields.items():
        result[field] = replaceMarkupInField(value, markup)

    return result


def buildFactMarkupExpression(expression, reading, glossary, sentence=None):
    return {
        '%e': expression, '%r': reading, '%g': glossary, '%s': sentence
    }


def buildFactMarkupReading(reading, glossary, sentence=None):
    return {
        '%e': reading, '%r': None, '%g': glossary, '%s': sentence
    }


def splitTags(tags):
    return re.split('[;,\s]', tags)


def convertDefinitions(definitions, sentence=None):
    return [
        Definition(*(definition + (sentence,))) for definition in definitions
    ]


def copyDefinitions(definitions):
    text = unicode()

    for definition in definitions:
        if definition.reading:
            text += u'{0}\t{1}\t{2}\n'.format(definition.expression, definition.reading, definition.glossary)
        else:
            text += u'{0}\t{1}\n'.format(definition.expression, definition.glossary)

    QtGui.QApplication.clipboard().setText(text)


def buildDefinitionHtml(definition, factIndex, factQuery):
    reading = unicode()
    if definition.reading:
        reading = u'[{0}]'.format(definition.reading)

    conjugation = unicode()
    if definition.conjugations:
        conjugation = '<span class = "conjugations">&lt;{0}&gt;<br/></span>'.format(definition.conjugations)

    links = '<a href = "copyDefinition:{0}"><img src = "{1}" align = "right"/></a>'.format(factIndex, buildResPath('img/page_copy.png'))
    if factQuery:
        if factQuery(buildFactMarkupExpression(definition.expression, definition.reading, definition.glossary)):
            links += '<a href = "addFactExpression:{0}"><img src = "{1}" align = "right"/></a>'.format(factIndex, buildResPath('img/add.png'))
        if factQuery(buildFactMarkupReading(definition.reading, definition.glossary)):
            links += '<a href = "addFactReading:{0}"><img src = "{1}" align = "right"/></a>'.format(factIndex, buildResPath('img/bullet_add.png'))

    html = u"""
        <span class = "links">{0}</span>
        <span class = "expression">{1}&nbsp;{2}<br/></span>
        <span class = "glossary">{3}<br/></span>
        <span class = "conjugation">{4}</span>
        <br clear = "all"/>""".format(links, definition.expression, reading, definition.glossary, conjugation)

    return html


def buildDefinitionsHtml(definitions, factQuery):
    palette = QtGui.QApplication.palette()
    toolTipBg = palette.color(QtGui.QPalette.Window).name()
    toolTipFg = palette.color(QtGui.QPalette.WindowText).name()

    html = u"""
        <html><head><style>
        body {{ background-color: {0}; color: {1}; font-size: 11pt; }}
        span.expression {{ font-size: 15pt; }}
        </style></head><body>""".format(toolTipBg, toolTipFg)

    if definitions:
        for i, definition in enumerate(definitions):
            html += buildDefinitionHtml(definition, i, factQuery)
    else:
        html += """
            <p>No definitions to display.</p>
            <p>Mouse over text with the <em>middle mouse button</em> or <em>shift key</em> pressed to search.</p>
            <p>You can also also input terms in the search box below.</p>"""

    html += '</body></html>'
    return html
