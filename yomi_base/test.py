# -*- coding: utf-8 -*-
from korean import initLanguage
from korean import deinflect
from time import time
import sys
deinflector = deinflect.Deinflector('korean/hangeul.js')
start = time()
result = deinflector.deinflect(u'반갑습니다',0)[1]['source']
print result == u'반갑다'
print time()-start