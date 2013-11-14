#/bin/sh

KANJIDIC=util/kanjidic
EDICT=util/edict
DICT=yomi_base/japanese/dictionary.db

rm $DICT
util/compile.py --kanjidic $KANJIDIC --edict $EDICT $DICT
