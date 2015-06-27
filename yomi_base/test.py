# -*- coding: utf-8 -*-
import sip
sip.setapi('QVariant', 2)
from PyQt4.QtGui import QApplication
from korean import initLanguage
from korean import deinflect
from time import time
import sys
app = QApplication(sys.argv)
#translator = initLanguage()
deinflector = deinflect.Deinflector('korean/hangeul.js')
start = time()
#print translator.deinflector.view.page().mainFrame().evaluateJavaScript('stemmer').toPyObject()
print len(deinflector.deinflect(u'기',0))
#translator.findTerm(u'기다렸어')
print time()-start