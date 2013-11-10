#/bin/sh

KANJIDIC=util/kanjidic
KRADFILE=util/kradfile
EDICT=util/edict
DICT=yomi_base/japanese/dictionary.db

rm $DICT
util/compile.py --kanjidic $KANJIDIC --kradfile $KRADFILE --edict $EDICT $DICT
