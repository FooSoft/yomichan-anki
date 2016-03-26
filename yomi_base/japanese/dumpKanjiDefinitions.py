#!/bin/python
 
import sqlite3
import json
 
def dict_factory(cursor, row):
    character = u''
    glossary = u''
    onyomi = u''
    for idx, col in enumerate(cursor.description):
        if col[0] == 'c':
            character = row[idx]
        elif col[0] == 'g':
            glossary = row[idx]
        elif col[0] == 'o':
            onyomi = row[idx]
    return (character,glossary,onyomi)
 
connection = sqlite3.connect("dictionary.db")
connection.row_factory = dict_factory
 
cursor = connection.cursor()
 
cursor.execute("select character as c, glossary as g, onyomi as o from Kanji")
 

d = dict()
for c, g, on in cursor.fetchall():
    d[c] = [g,on]
 
print json.dumps(d, separators=(',',':'))
 
connection.close()
