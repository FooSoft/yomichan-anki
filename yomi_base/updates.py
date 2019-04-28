# -*- coding: utf-8 -*-

# Copyright (C) 2013  Alex Yatskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from PyQt4 import QtCore, QtGui
import constants
import gen.updates_ui
import json
import urllib2


class DialogUpdates(QtGui.QDialog, gen.updates_ui.Ui_DialogUpdates):
    def __init__(self, parent, versions):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.updateHtml(versions)
        self.labelUpdates.setText(
            unicode(self.labelUpdates.text()).format(
                constants.c['appVersion'],
                versions['latest']
            )
        )


    def updateHtml(self, versions):
        html = '<html><body>'

        for update in versions['updates']:
            version = update.get('version')
            if version > constants.c['appVersion']:
                html += '<strong>Version {0}</strong>'.format(version)
                html += '<ul>'
                for feature in update['features']:
                    html += '<li>{0}</li>'.format(feature)
                html += '</ul>'

        self.textBrowser.setHtml(html)


class UpdateFinder(QtCore.QThread):
    updateResult = QtCore.pyqtSignal(dict)

    def run(self):
        latest = constants.c['appVersion']
        updates = []

        try:
            fp = urllib2.urlopen('https://foosoft.net/projects/yomichan/dl/updates.json')
            updates = json.loads(fp.read())
            fp.close()

            for update in updates:
                latest = max(latest, update.get('version'))
        except:
            pass
        finally:
            self.updateResult.emit({'latest': latest, 'updates': updates})
