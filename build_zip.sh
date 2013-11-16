#!/bin/sh

ZIP=yomichan.zip

[ -f $ZIPFILE ] rm $ZIP
7z a yomichan.zip -xr\!\*.pyc yomichan.py yomi_base
