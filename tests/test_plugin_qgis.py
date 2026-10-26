# -*- coding: utf-8 -*-
"""End-to-end test of the plugin inside PyQGIS (QGIS 3 / Qt5 or QGIS 4 / Qt6).

Skipped when PyQGIS is not installed.  Run headless with
    QT_QPA_PLATFORM=offscreen python -m unittest tests.test_plugin_qgis -v
"""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

try:
    from qgis.core import QgsApplication, QgsProject
    from qgis.PyQt.QtCore import QT_VERSION_STR
    HAVE_QGIS = True
except ImportError:  # pragma: no cover
    HAVE_QGIS = False

_APP = None


def _app():
    global _APP
    if _APP is None:
        _APP = QgsApplication.instance()   # another test module may have one
    if _APP is None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        _APP = QgsApplication([], True)
        _APP.initQgis()
    return _APP


@unittest.skipUnless(HAVE_QGIS, "PyQGIS not available")
class PluginTests(unittest.TestCase):
    def setUp(self):
        _app()
        from osgeo import ogr
        import test_merge_core as t
        self.ogr = ogr
        self.tmp = tempfile.mkdtemp()
        self.a = os.path.join(self.tmp, "鑽孔A.gpkg")
        self.b = os.path.join(self.tmp, "site-B.gpkg")
        self.c = os.path.join(self.tmp, "c.gpkg")
        t._make_gpkg(self.a, [("boreholes", t.PT, 3826, t.F_STD, 3),
                              ("roads", ogr.wkbLineString, 3826, [], 0)],
                     styles=[("boreholes", "<qgis/>")])
        t._make_gpkg(self.b, [("Boreholes", t.PT, 3826, t.F_STD, 5),
                              ("wells", t.PT, 3826, t.F_STD, 1)])
        t._make_gpkg(self.c, [("boreholes", t.PT, 4326,
                               t.F_STD + [("depth", ogr.OFTReal)], 4)])
        self.out = os.path.join(self.tmp, "merged.gpkg")

    def tearDown(self):
        QgsProject.instance().removeAllMapLayers()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _layers(self):
        ds = self.ogr.Open(self.out)
        return {ds.GetLayerByIndex(i).GetName(): ds.GetLayerByIndex(i).GetFeatureCount()
                for i in range(ds.GetLayerCount())}

    def _plugin(self, lang):
        import gpkg_merger.plugin as P
        from qgis.PyQt.QtWidgets import QMainWindow
        iface = mock.MagicMock()
        self.win = QMainWindow()
        iface.mainWindow.return_value = self.win
        with mock.patch.object(P, "qgis_locale", return_value=lang):
            plugin = P.GpkgMergerPlugin(iface)
        plugin.initGui()
        return plugin

    def test_translation_follows_locale(self):
        expected = {"zh-Hant": "合併 GeoPackage…", "zh_CN": "合并 GeoPackage…",
                    "ja": "GeoPackage を結合…", "de_DE": "GeoPackages zusammenführen…",
                    "en_US": "Merge GeoPackages…"}
        for lang, text in expected.items():
            plugin = self._plugin(lang)
            self.assertEqual(plugin.action.text(), text, lang)
            plugin.unload()

    def test_dialog_all_modes(self):
        from qgis.PyQt.QtWidgets import QMessageBox
        print("Qt", QT_VERSION_STR, "QGIS", QgsApplication.instance().applicationVersion()
              if hasattr(QgsApplication.instance(), "applicationVersion") else "")
        plugin = self._plugin("en_US")
        plugin.run()
        dlg = plugin.dialog
        dlg._add_files([self.a, self.b, self.c])
        self.assertEqual(dlg.list_files.count(), 3)
        dlg.file_out.setFilePath(self.out)
        warnings = []
        with mock.patch.object(QMessageBox, "warning",
                               side_effect=lambda *a, **k: warnings.append(a[2])), \
                mock.patch.object(QMessageBox, "question",
                                  return_value=QMessageBox.StandardButton.Yes):
            dlg.rb_rename.setChecked(True)
            dlg._refresh()
            dlg._run()
            self.assertIn("鑽孔A_boreholes", self._layers())
            self.assertIn("site_B_Boreholes", self._layers())

            dlg.rb_overwrite.setChecked(True)
            dlg._refresh()
            dlg._run()
            self.assertEqual(self._layers()["boreholes"], 4)  # c.gpkg is last

            dlg.rb_append.setChecked(True)
            dlg._refresh()
            before = os.path.getmtime(self.out)
            dlg._run()
            self.assertTrue(warnings, "incompatible append must be blocked")
            self.assertEqual(os.path.getmtime(self.out), before)

            dlg.list_files.setCurrentRow(2)
            dlg._remove_selected()
            dlg._run()
            self.assertEqual(self._layers()["boreholes"], 8)

        # re-ordering: move row 1 to the top
        dlg.list_files.setCurrentRow(1)
        dlg._move(-1)
        self.assertEqual(os.path.basename(dlg.paths()[0]), "site-B.gpkg")
        self.assertGreater(len(QgsProject.instance().mapLayers()), 0)
        plugin.unload()

    def test_dialog_full_content(self):
        from rich_fixture import make_rich_gpkg
        a = make_rich_gpkg(os.path.join(self.tmp, "rich_a.gpkg"))
        b = make_rich_gpkg(os.path.join(self.tmp, "rich_b.gpkg"), x0=251000.0)
        plugin = self._plugin("zh-Hant")
        plugin.run()
        dlg = plugin.dialog
        dlg._add_files([a, b])
        dlg.rb_rename.setChecked(True)
        dlg._refresh()
        top = dlg.tree.topLevelItem(0)
        rows = {top.child(i).text(0): top.child(i).text(1) for i in range(top.childCount())}
        self.assertEqual(rows["survey"], "QGIS 專案")
        self.assertEqual(rows["ortho"], "網格（圖磚）")
        self.assertEqual(rows["v_core"], "檢視表")
        dlg.file_out.setFilePath(self.out)
        dlg.show()
        QgsApplication.processEvents()
        shot = os.environ.get("GPKG_MERGER_SCREENSHOT")
        if shot:
            dlg.grab().save(shot)
        dlg._run()
        names = {lyr.name() for lyr in QgsProject.instance().mapLayers().values()}
        self.assertIn("rich_a_ortho", names)       # rasters are loaded too
        self.assertIn("rich_b_boreholes", names)
        plugin.unload()


if __name__ == "__main__":
    unittest.main()
