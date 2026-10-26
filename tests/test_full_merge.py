# -*- coding: utf-8 -*-
"""Merging *everything* in a GeoPackage: rasters, DEMs, plain tables, views,
metadata, styles and QGIS projects, in all three conflict modes.

The QGIS project parts need PyQGIS; without it they are skipped and the
fixtures are built without projects/styles/QGIS metadata.
"""
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

from osgeo import gdal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from gpkg_merger import merge_core as mc  # noqa: E402
from rich_fixture import make_rich_gpkg  # noqa: E402

try:
    from qgis.core import QgsApplication, QgsProject, QgsVectorLayer
    HAVE_QGIS = True
except ImportError:  # pragma: no cover
    HAVE_QGIS = False

_APP = []


def setUpModule():
    if HAVE_QGIS and QgsApplication.instance() is None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        app = QgsApplication([], True)
        app.initQgis()
        _APP.append(app)


class FullMergeTests(unittest.TestCase):
    def setUp(self):
        gdal.UseExceptions()
        self.tmp = tempfile.mkdtemp()
        # same object names in both files -> every object is a conflict
        self.a = make_rich_gpkg(os.path.join(self.tmp, "a.gpkg"), with_qgis=HAVE_QGIS)
        self.b = make_rich_gpkg(os.path.join(self.tmp, "b.gpkg"), with_qgis=HAVE_QGIS,
                                x0=251000.0)
        os.makedirs(os.path.join(self.tmp, "out"))
        self.out = os.path.join(self.tmp, "out", "merged.gpkg")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _merge(self, mode):
        plan = mc.build_plan([mc.scan_gpkg(self.a), mc.scan_gpkg(self.b)], mode)
        self.assertTrue(plan.ok, plan.errors)
        mc.execute_plan(plan, self.out)
        return plan

    def _sql(self, sql, params=()):
        con = sqlite3.connect(self.out)
        try:
            return con.execute(sql, params).fetchall()
        finally:
            con.close()

    def _contents(self):
        return dict(self._sql("SELECT table_name, data_type FROM gpkg_contents"))

    def _validate(self):
        try:
            from osgeo_utils.samples import validate_gpkg
        except ImportError:
            return
        validate_gpkg.check(self.out)

    def _raster_ok(self, table, value):
        ds = gdal.Open("GPKG:{0}:{1}".format(self.out, table))
        self.assertEqual(ds.GetRasterBand(1).ComputeRasterMinMax(False), (value, value))

    def _project_layers(self, name):
        p = QgsProject()
        self.assertTrue(p.read("geopackage:{0}?projectName={1}".format(self.out, name)))
        out = {}
        for lyr in p.mapLayers().values():
            self.assertTrue(lyr.isValid(), lyr.source())
            self.assertIn(os.path.basename(self.out), lyr.source())
            self.assertNotIn("a.gpkg", lyr.source())
            out[lyr.name()] = lyr.source()
        return out

    def test_scan_finds_everything(self):
        src = mc.scan_gpkg(self.a)
        kinds = {l.name: l.kind for l in src.layers}
        self.assertEqual(kinds["boreholes"], mc.KIND_FEATURES)
        self.assertEqual(kinds["logs"], mc.KIND_ATTRIBUTES)
        self.assertEqual(kinds["ortho"], mc.KIND_TILES)
        self.assertEqual(kinds["dem"], mc.KIND_TILES)
        self.assertEqual(kinds["notes"], mc.KIND_TABLE)
        self.assertEqual(kinds["v_core"], mc.KIND_VIEW)
        if HAVE_QGIS:
            self.assertEqual(src.projects, ["survey"])

    def test_rename_keeps_every_object(self):
        self._merge(mc.MODE_RENAME)
        c = self._contents()
        for name, dtype in [("a_boreholes", "features"), ("b_boreholes", "features"),
                            ("a_logs", "attributes"), ("a_ortho", "tiles"),
                            ("b_ortho", "tiles"), ("a_dem", "2d-gridded-coverage"),
                            ("b_dem", "2d-gridded-coverage")]:
            self.assertEqual(c.get(name), dtype, name)
        self._raster_ok("b_ortho", 60.0)
        self._raster_ok("a_dem", 123.25)
        self.assertEqual(self._sql('SELECT txt FROM "b_notes"'), [("hello",)])
        # the view was rewritten to the renamed table
        self.assertEqual(len(self._sql('SELECT * FROM "a_v_core"')), 2)
        self._validate()
        if HAVE_QGIS:
            self.assertEqual(sorted(r[0] for r in self._sql("SELECT name FROM qgis_projects")),
                             ["a_survey", "b_survey"])
            srcs = self._project_layers("b_survey")
            self.assertTrue(srcs["Boreholes"].endswith("|layername=b_boreholes"))
            self.assertTrue(srcs["Ortho"].endswith(":b_ortho"))
            vl = QgsVectorLayer(self.out + "|layername=a_boreholes", "x", "ogr")
            self.assertEqual(vl.metadata().title(), "QGIS metadata boreholes")
            self.assertEqual(vl.renderer().symbol().color().name(), "#d81b60")

    def test_overwrite_later_file_wins(self):
        plan = self._merge(mc.MODE_OVERWRITE)
        c = self._contents()
        self.assertIn("ortho", c)
        self.assertNotIn("a_ortho", c)
        # boreholes come from b.gpkg (x0 = 251000)
        self.assertTrue(plan.notes)
        ds = gdal.OpenEx(self.out)
        lyr = ds.GetLayerByName("boreholes")
        self.assertGreaterEqual(lyr.GetExtent()[0], 251000.0)
        ds = None
        self._validate()
        if HAVE_QGIS:
            self.assertEqual(self._sql("SELECT name FROM qgis_projects"), [("survey",)])
            srcs = self._project_layers("survey")
            self.assertTrue(srcs["Boreholes"].endswith("|layername=boreholes"))

    def test_append_vectors_and_keep_the_rest(self):
        plan = self._merge(mc.MODE_APPEND)
        c = self._contents()
        ds = gdal.OpenEx(self.out)
        self.assertEqual(ds.GetLayerByName("boreholes").GetFeatureCount(), 6)
        self.assertEqual(ds.GetLayerByName("logs").GetFeatureCount(), 8)
        ds = None
        # rasters / tables / views cannot be appended -> renamed
        self.assertIn("a_ortho", c)
        self.assertIn("b_dem", c)
        self.assertEqual(len(self._sql('SELECT * FROM "b_notes"')), 1)
        self.assertTrue(any("only vector" in n for n in plan.notes))
        # views point to the appended table and see both files' rows
        self.assertEqual(len(self._sql('SELECT * FROM "a_v_core"')), 4)
        self._validate()
        if HAVE_QGIS:
            for name in ("a_survey", "b_survey"):
                srcs = self._project_layers(name)
                self.assertTrue(srcs["Boreholes"].endswith("|layername=boreholes"))

    def test_project_rewriter_formats(self):
        from gpkg_merger.project_rewrite import SourceRewriter
        out = os.path.join(self.tmp, "out", "m.gpkg")
        rw = SourceRewriter([{"path": self.a, "tables": {"roads": "a_roads"},
                              "ogr_order": ["pts", "roads"]}], out)
        d = self.tmp
        self.assertEqual(rw.rewrite("./a.gpkg|layername=roads", d), "./m.gpkg|layername=a_roads")
        self.assertEqual(rw.rewrite("./a.gpkg|layerid=1|subset=x", d),
                         "./m.gpkg|layername=a_roads|subset=x")
        self.assertEqual(rw.rewrite(self.a + "|layername=pts", "/elsewhere"),
                         out + "|layername=pts")
        self.assertEqual(rw.rewrite("GPKG:./a.gpkg:roads", d), "GPKG:./m.gpkg:a_roads")
        self.assertEqual(rw.rewrite("./other.gpkg|layername=roads", d),
                         "./other.gpkg|layername=roads")
        xml = '<x source="./a.gpkg|layername=roads"><datasource>./a.gpkg|layername=roads</datasource></x>'
        self.assertEqual(rw.rewrite_xml(xml, d).count("m.gpkg|layername=a_roads"), 2)


if __name__ == "__main__":
    unittest.main()
