call pyuic4 ui/about.ui -o yomi_base/gen/about_ui.py
call pyuic4 ui/preferences.ui -o yomi_base/gen/preferences_ui.py
call pyuic4 ui/reader.ui -o yomi_base/gen/reader_ui.py
call pyuic4 ui/updates.ui -o yomi_base/gen/updates_ui.py
call pyrcc4 ui/resources.qrc -o yomi_base/gen/resources_rc.py
