# -*- coding: utf-8 -*-
"""Tests for the merge engine.  Run with:  python -m pytest tests
(needs the GDAL Python bindings, no QGIS required)."""
import os
import sys
import tempfile
import unittest
from unittest import mock

from osgeo import ogr, osr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gpkg_merger import merge_core as mc  # noqa: E402


def _make_gpkg(path, layers, styles=None):
    """layers: list of (name, geom_type, epsg, [(field, type)], n_features)"""
    drv = ogr.GetDriverByName("GPKG")
    ds = drv.CreateDataSource(path)
    for name, gtype, epsg, fields, n in layers:
        srs = None
        if epsg:
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(epsg)
        lyr = ds.CreateLayer(name, srs, gtype)
        for fname, ftype in fields:
            lyr.CreateField(ogr.FieldDefn(fname, ftype))
        for i in range(n):
            f = ogr.Feature(lyr.GetLayerDefn())
            for fname, ftype in fields:
                f.SetField(fname, i if ftype == ogr.OFTInteger else "v%d" % i)
            if gtype != ogr.wkbNone:
                g = ogr.Geometry(ogr.wkbPoint)
                g.AddPoint_2D(120.0 + i, 23.0)
                f.SetGeometry(g)
            lyr.CreateFeature(f)
    if styles:
        lyr = ds.CreateLayer("layer_styles", None, ogr.wkbNone, ["FID=id"])
        for col in ("f_table_catalog", "f_table_schema", "f_table_name",
                    "f_geometry_column", "styleName", "styleQML"):
            lyr.CreateField(ogr.FieldDefn(col, ogr.OFTString))
        lyr.CreateField(ogr.FieldDefn("useAsDefault", ogr.OFTInteger))
        for table, qml in styles:
            f = ogr.Feature(lyr.GetLayerDefn())
            f.SetField("f_table_name", table)
            f.SetField("f_geometry_column", "geom")
            f.SetField("styleName", table)
            f.SetField("styleQML", qml)
            f.SetField("useAsDefault", 1)
            lyr.CreateFeature(f)
    ds = None


def _layers(path):
    ds = ogr.Open(path)
    out = {}
    for i in range(ds.GetLayerCount()):
        lyr = ds.GetLayerByIndex(i)
        out[lyr.GetName()] = lyr.GetFeatureCount()
    return out


PT = ogr.wkbPoint
F_STD = [("name", ogr.OFTString), ("code", ogr.OFTInteger)]


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.a = os.path.join(self.tmp, "鑽孔A.gpkg")
        self.b = os.path.join(self.tmp, "site-B.gpkg")
        self.c = os.path.join(self.tmp, "c.gpkg")
        _make_gpkg(self.a, [("boreholes", PT, 3826, F_STD, 3),
                            ("roads", ogr.wkbLineString, 3826, [], 0),
                            ("notes", ogr.wkbNone, None, [("txt", ogr.OFTString)], 2)],
                   styles=[("boreholes", "<qgis>A</qgis>"), ("roads", "<qgis>R</qgis>")])
        _make_gpkg(self.b, [("Boreholes", PT, 3826, F_STD, 5),
                            ("wells", PT, 3826, F_STD, 1)],
                   styles=[("Boreholes", "<qgis>B</qgis>")])
        # incompatible: other CRS and extra field
        _make_gpkg(self.c, [("boreholes", PT, 4326, F_STD + [("depth", ogr.OFTReal)], 4)])
        self.out = os.path.join(self.tmp, "out.gpkg")

    def _scan(self, *paths):
        return [mc.scan_gpkg(p) for p in paths]

    def test_scan(self):
        a = mc.scan_gpkg(self.a)
        self.assertTrue(a.has_styles)
        self.assertEqual([l.name for l in a.layers], ["boreholes", "roads", "notes"])

    def test_conflicts_case_insensitive(self):
        conf = mc.find_conflicts(self._scan(self.a, self.b))
        self.assertEqual(list(conf), ["boreholes"])

    def test_rename(self):
        plan = mc.build_plan(self._scan(self.a, self.b), mc.MODE_RENAME)
        self.assertTrue(plan.ok)
        mc.execute_plan(plan, self.out)
        lyrs = _layers(self.out)
        self.assertEqual(lyrs["鑽孔A_boreholes"], 3)
        self.assertEqual(lyrs["site_B_Boreholes"], 5)
        self.assertEqual(lyrs["wells"], 1)
        self.assertEqual(lyrs["notes"], 2)
        self.assertNotIn("boreholes", {k.lower() for k in lyrs if k.lower() == "boreholes"})
        # styles follow the renamed layers
        ds = ogr.Open(self.out)
        st = ds.GetLayerByName("layer_styles")
        names = sorted(f.GetField("f_table_name") for f in st)
        self.assertGreaterEqual(st.GetLayerDefn().GetFieldIndex("update_time"), 0)
        self.assertEqual(names, ["roads", "site_B_Boreholes", "鑽孔A_boreholes"])

    def test_overwrite_later_wins(self):
        plan = mc.build_plan(self._scan(self.a, self.b), mc.MODE_OVERWRITE)
        mc.execute_plan(plan, self.out)
        lyrs = _layers(self.out)
        self.assertEqual(lyrs["Boreholes"], 5)
        self.assertNotIn("boreholes", lyrs)
        # reversed order: A wins
        plan = mc.build_plan(self._scan(self.b, self.a), mc.MODE_OVERWRITE)
        mc.execute_plan(plan, self.out)
        self.assertEqual(_layers(self.out)["boreholes"], 3)
        ds = ogr.Open(self.out)
        qml = [f.GetField("styleQML") for f in ds.GetLayerByName("layer_styles")
               if f.GetField("f_table_name") == "boreholes"]
        self.assertEqual(qml, ["<qgis>A</qgis>"])

    def test_append(self):
        plan = mc.build_plan(self._scan(self.a, self.b), mc.MODE_APPEND)
        self.assertTrue(plan.ok, plan.errors)
        mc.execute_plan(plan, self.out)
        lyrs = _layers(self.out)
        self.assertEqual(lyrs["boreholes"], 8)
        ds = ogr.Open(self.out)
        lyr = ds.GetLayerByName("boreholes")
        fids = [f.GetFID() for f in lyr]
        self.assertEqual(len(set(fids)), 8)
        self.assertEqual(lyr.GetSpatialRef().GetAuthorityCode(None), "3826")

    def test_append_incompatible_stops(self):
        plan = mc.build_plan(self._scan(self.a, self.c), mc.MODE_APPEND)
        self.assertFalse(plan.ok)
        msg = plan.errors[0]
        self.assertIn("coordinate reference system", msg)
        self.assertIn("depth", msg)
        with self.assertRaises(mc.MergeError):
            mc.execute_plan(plan, self.out)
        self.assertFalse(os.path.exists(self.out))

    def test_output_must_differ(self):
        plan = mc.build_plan(self._scan(self.a, self.b), mc.MODE_RENAME)
        with self.assertRaises(mc.MergeError):
            mc.execute_plan(plan, self.a)

    def test_cancel(self):
        plan = mc.build_plan(self._scan(self.a, self.b), mc.MODE_RENAME)
        with self.assertRaises(mc.MergeCancelled):
            mc.execute_plan(plan, self.out, progress=lambda f: False)
        self.assertFalse(os.path.exists(self.out))
        self.assertFalse(os.path.exists(self.out + ".partial.gpkg"))

    def test_same_stem_and_name_collision(self):
        d2 = os.path.join(self.tmp, "sub")
        os.mkdir(d2)
        a2 = os.path.join(d2, "鑽孔A.gpkg")
        # also contains a layer already named like the generated one
        _make_gpkg(a2, [("boreholes", PT, 3826, F_STD, 1),
                        ("鑽孔A_boreholes", PT, 3826, F_STD, 1)])
        plan = mc.build_plan(self._scan(self.a, a2), mc.MODE_RENAME)
        outs = [s.out_name for s in plan.steps]
        self.assertEqual(len(outs), len({o.lower() for o in outs}))
        mc.execute_plan(plan, self.out)
        self.assertEqual(len(_layers(self.out)), len(outs) + 1)  # + layer_styles


class _NoUriConnection(object):
    """Mimics SQLite builds without SQLITE_USE_URI (Python in QGIS on
    Windows): 'file:' names in ATTACH only work when the connection was
    opened with uri=True.  With fail_uri=True every URI is rejected, like a
    Windows network path (file://server/share/...)."""

    def __init__(self, con, uri, fail_uri):
        self._con, self._uri, self._fail = con, uri, fail_uri

    def execute(self, sql, params=()):
        if sql.lstrip().upper().startswith("ATTACH") and str(params[0]).startswith("file:"):
            if self._fail or not self._uri:
                import sqlite3
                raise sqlite3.OperationalError(
                    "unable to open database: " + str(params[0]))
        return self._con.execute(sql, params)

    def __getattr__(self, name):
        return getattr(self._con, name)


class WindowsSqliteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.a = os.path.join(self.tmp, "a.gpkg")
        self.b = os.path.join(self.tmp, "b.gpkg")
        _make_gpkg(self.a, [("pts", PT, 3826, F_STD, 2)])
        _make_gpkg(self.b, [("pts", PT, 3826, F_STD, 3)])
        import sqlite3
        con = sqlite3.connect(self.a)
        con.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, txt TEXT)")
        con.execute("INSERT INTO notes (txt) VALUES ('x')")
        con.commit()
        con.close()
        self.out = os.path.join(self.tmp, "out.gpkg")

    def _run(self, fail_uri):
        import sqlite3
        real = sqlite3.connect

        def fake(database, *args, **kwargs):
            if fail_uri and str(database).startswith("file:"):
                raise sqlite3.OperationalError("invalid uri authority")
            return _NoUriConnection(real(database, *args, **kwargs),
                                    kwargs.get("uri", False), fail_uri)

        sources = [mc.scan_gpkg(self.a), mc.scan_gpkg(self.b)]
        plan = mc.build_plan(sources, mc.MODE_RENAME)
        with mock.patch.object(mc.sqlite3, "connect", side_effect=fake):
            mc.execute_plan(plan, self.out)
        con = sqlite3.connect(self.out)
        self.assertEqual(con.execute("SELECT txt FROM notes").fetchall(), [("x",)])
        con.close()

    def test_sqlite_without_uri_support(self):
        self._run(fail_uri=False)

    def test_uri_not_usable_falls_back_to_path(self):
        self._run(fail_uri=True)


if __name__ == "__main__":
    unittest.main()
