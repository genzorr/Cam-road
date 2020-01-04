#!/bin/bash
rm -f window.py
rm -f workwidget.py
rm -f settingswidget.py
rm -f telemetrywidget.py
pyuic5 -x window.ui -o window.py
pyuic5 -x workwidget.ui -o workwidget.py
pyuic5 -x settingswidget.ui -o settingswidget.py
pyuic5 -x telemetrywidget.ui -o telemetrywidget.py
