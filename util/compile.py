#!/usr/bin/env python

import os
import re
import sys
import codecs
import sqlite3


GRAMMAR_TAGS = {
    'adj-i',    # adjective (keiyoushi)
    'adj-na',   # adjectival nouns or quasi-adjectives (keiyodoshi)
    'adj-no',   # nouns which may take the genitive case particle `no'
    'adj-pn',   # pre-noun adjectival (rentaishi)
    'adj-t',    # `taru' adjective
    'adj-f',    # noun or verb acting prenominally (other than the above)
    'adj',      # former adjective classification (being removed)
    'adv',      # adverb (fukushi)
    'adv-n',    # adverbial noun
    'adv-to',   # adverb taking the `to' particle
    'aux',      # auxiliary
    'aux-v',    # auxiliary verb
    'aux-adj',  # auxiliary adjective
    'conj',     # conjunction
    'ctr',      # counter
    'exp',      # Expressions (phrases, clauses, etc.)
    'int',      # interjection (kandoushi)
    'iv',       # irregular verb
    'n',        # noun (common) (futsuumeishi)
    'n-adv',    # adverbial noun (fukushitekimeishi)
    'n-pref',   # noun, used as a prefix
    'n-suf',    # noun, used as a suffix
    'n-t',      # noun (temporal) (jisoumeishi)
    'num',      # numeric
    'pn',       # pronoun
    'pref' ,    # prefix
    'prt',      # particle
    'suf',      # suffix
    'v1',       # Ichidan verb
    'v2a-s',    # Nidan verb with 'u' ending (archaic)
    'v4h',      # Yodan verb with `hu/fu' ending (archaic)
    'v4r',      # Yodan verb with `ru' ending (archaic)
    'v5',       # Godan verb (not completely classified)
    'v5aru',    # Godan verb - -aru special class
    'v5b',      # Godan verb with `bu' ending
    'v5g',      # Godan verb with `gu' ending
    'v5k',      # Godan verb with `ku' ending
    'v5k-s',    # Godan verb - iku/yuku special class
    'v5m',      # Godan verb with `mu' ending
    'v5n',      # Godan verb with `nu' ending
    'v5r',      # Godan verb with `ru' ending
    'v5r-i',    # Godan verb with `ru' ending (irregular verb)
    'v5s',      # Godan verb with `su' ending
    'v5t',      # Godan verb with `tsu' ending
    'v5u',      # Godan verb with `u' ending
    'v5u-s',    # Godan verb with `u' ending (special class)
    'v5uru',    # Godan verb - uru old class verb (old form of Eru)
    'v5z',      # Godan verb with `zu' ending
    'vz',       # Ichidan verb - zuru verb - (alternative form of -jiru verbs)
    'vi',       # intransitive verb
    'vk',       # kuru verb - special class
    'vn',       # irregular nu verb
    'vs',       # noun or participle which takes the aux. verb suru
    'vs-c',     # su verb - precursor to the modern suru
    'vs-i',     # suru verb - irregular
    'vs-s',     # suru verb - special class
    'vt',       # transitive verb
}

def isHiragana(c):
    return 0x3040 <= ord(c) < 0x30a0


def isKatakana(c):
    return 0x30a0 <= ord(c) < 0x3100


def loadDefinitions(path):
    print 'Parsing "{0}"...'.format(path)
    with codecs.open(path, encoding='euc-jp') as fp:
        return filter(lambda x: x and x[0] != '#', fp.read().splitlines())


def parseKanjiDic(path):
    results = list()

    for line in loadDefinitions('kanjidic'):
        segments = line.split()
        results.append({
            'character': segments[0],
            'onyomi': filter(lambda x: filter(isKatakana, x), segments[1:]),
            'kunyomi': filter(lambda x: filter(isHiragana, x), segments[1:]),
            'meanings': re.findall('\{([^\}]+)\}', line)
        })

    return results


def writeKanjiDic(cursor, values):
    pass


def parseKradFile(path):
    radsByChar = dict()
    charsByRad = dict()

    for line in loadDefinitions(path):
        segments = line.split(' ')
        character = segments[0]
        radicals = segments[2:]

        radsByChar[character] = radicals
        for radical in radicals:
            charsByRad[radical] = charsByRad.get(radical, list()) + [character]

    results = {
        'radsByChar': radsByChar,
        'charsByRad': charsByRad
    }

    return results


def writeKradFile(cursor, values):
    pass


def parseEdict(path):
    results = list()

    for line in loadDefinitions(path):
        segments = line.split('/')

        expression = segments[0].split(' ')
        term = expression[0]
        match = re.search('\[([^\]]+)\]', expression[1])
        reading = None if match is None else match.group(1)

        definitions = filter(lambda x: len(x) > 0, segments[1:])
        definitions = '; '.join(definitions)
        definitions = re.sub('\(\d+\)\s*', str(), definitions)

        tags = list()
        for group in re.findall('\(([^\)\]]+)\)', definitions):
            tags.extend(group.split(','))

        tags = set(tags).intersection(GRAMMAR_TAGS)
        tags = ','.join(sorted(tags))

        results.append((term, reading, definitions, tags))

    return results


def writeEdict(cursor, values):
    cursor.execute('drop table if exists Edict')
    cursor.execute('create table Edict(term text, reading text, definitions text, tags text)')
    cursor.executemany('insert into Edict values(?, ?, ?, ?)', values)


def main(path, kanjidic=None, kradfile=None, edict=None):
    with sqlite3.connect(path) as db:
        cursor = db.cursor()

        if kanjidic is not None:
            writeKanjiDic(cursor, parseKanjiDic(kanjidic))

        if kradfile is not None:
            writeKradFile(cursor, parseKradFile(kradfile))

        if edict is not None:
            writeEdict(cursor, parseEdict(edict))


if __name__ == '__main__':
    main('dictionary.db', edict='data/edict')
