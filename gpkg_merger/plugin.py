# -*- coding: utf-8 -*-
"""QGIS plugin class: loads the translation matching the QGIS UI language
and adds the menu / toolbar entry."""

import os

from qgis.core import QgsApplication, QgsSettings
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QTranslator
from qgis.PyQt.QtGui import QIcon

try:  # Qt6 / QGIS 4: QAction lives in QtGui
    from qgis.PyQt.QtGui import QAction
except ImportError:  # Qt5 / QGIS 3
    from qgis.PyQt.QtWidgets import QAction

from .i18n_util import normalize_locale, tr

PLUGIN_DIR = os.path.dirname(__file__)


def qgis_locale():
    """The language QGIS itself is displayed in (Settings ▸ Options ▸ General
    ▸ Override system locale), falling back to the system locale."""
    if hasattr(QgsApplication, "locale"):
        loc = QgsApplication.locale()
        if loc:
            return loc
    settings = QgsSettings()
    if settings.value("locale/overrideFlag", False, type=bool):
        loc = settings.value("locale/userLocale", "", type=str)
        if loc:
            return loc
    return QLocale.system().name()


class GpkgMergerPlugin(object):
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None
        self.translator = None
        self._load_translation()

    def _load_translation(self):
        lang = normalize_locale(qgis_locale())
        if lang == "en":
            return
        qm = os.path.join(PLUGIN_DIR, "i18n", "gpkg_merger_{0}.qm".format(lang))
        if os.path.exists(qm):
            self.translator = QTranslator()
            if self.translator.load(qm):
                QCoreApplication.installTranslator(self.translator)
            else:
                self.translator = None

    def initGui(self):  # noqa: N802
        icon = QIcon(os.path.join(PLUGIN_DIR, "icon.png"))
        self.action = QAction(icon, tr("Merge GeoPackages…"), self.iface.mainWindow())
        self.action.setToolTip(tr("Merge several GeoPackage files into one"))
        self.action.triggered.connect(self.run)
        self.iface.addPluginToVectorMenu(tr("&GPKG Merger"), self.action)
        self.iface.addVectorToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removePluginVectorMenu(tr("&GPKG Merger"), self.action)
            self.iface.removeVectorToolBarIcon(self.action)
            self.action.deleteLater()
            self.action = None
        if self.dialog:
            self.dialog.close()
            self.dialog.deleteLater()
            self.dialog = None
        if self.translator:
            QCoreApplication.removeTranslator(self.translator)
            self.translator = None

    def run(self):
        from .dialog import GpkgMergerDialog
        if self.dialog is None:
            self.dialog = GpkgMergerDialog(self.iface, self.iface.mainWindow())
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
