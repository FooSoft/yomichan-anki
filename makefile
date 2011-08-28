all: \
	core/resources_rc.py \
	core/reader_ui.py \
	core/preferences_ui.py \
	core/about_ui.py

clean:
	hg st -nu | xargs rm

core/resources_rc.py: dev/resources.qrc
	pyrcc4 $< -o $@

core/reader_ui.py: dev/reader.ui
	pyuic4 $< -o $@

core/preferences_ui.py: dev/preferences.ui
	pyuic4 $< -o $@

core/about_ui.py: dev/about.ui
	pyuic4 $< -o $@
