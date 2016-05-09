#!/bin/sh

KANJIDIC=common/data/kanjidic
EDICT=common/data/edict
ENAMDICT=common/data/enamdict
DB=yomi_base/japanese/dictionary.db

common/compile.py --kanjidic $KANJIDIC --edict $EDICT $DICT --enamdict $ENAMDICT --db $DB
