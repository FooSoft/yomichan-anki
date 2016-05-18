#!/bin/sh
ZIP=yomichan.zip
rm -f $ZIP
7z a yomichan.zip -xr\!\*.pyc yomichan.py yomi_base
