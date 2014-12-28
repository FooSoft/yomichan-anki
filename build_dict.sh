#!/bin/sh

KANJIDIC=util/kanjidic
EDICT=util/edict
ENAMDICT=util/enamdict
DICT=yomi_base/japanese/dictionary.db

[ -f $DICT ] && rm $DICT
util/compile.py --kanjidic $KANJIDIC --edict $EDICT $DICT --enamdict $ENAMDICT
