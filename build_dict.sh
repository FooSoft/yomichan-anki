#!/bin/sh

KANJIDIC=util/data/kanjidic
KRADFILE=util/data/kradfile
EDICT=util/data/edict
DICT=yomi_base/japanese2/data/dictionary.db

rm $DICT
util/compile.py --kanjidic $KANJIDIC --kradfile $KRADFILE --edict $EDICT $DICT
