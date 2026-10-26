# -*- coding: utf-8 -*-
"""Build a GeoPackage that contains (almost) every kind of object a QGIS
user can store in one: vector + attribute tables, field aliases / comments /
domains, a relationship, GDAL and QGIS layer metadata, layer styles, an RGB
tile pyramid, a gridded coverage (DEM), a plain table, a view and a QGIS
project.

Needs PyQGIS for the project / styles / QGIS metadata parts; everything
else only needs GDAL.  Used by tests/test_full_merge.py.
"""
import os
import sqlite3

from osgeo import gdal, ogr, osr


def make_rich_gpkg(path, prefix="", epsg=3826, project_name="survey", with_qgis=True,
                   x0=250000.0, y0=2600000.0):
    """prefix lets two fixtures share or not share object names."""
    gdal.UseExceptions()
    ogr.UseExceptions()
    if os.path.exists(path):
        os.remove(path)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    ds = gdal.GetDriverByName("GPKG").Create(path, 0, 0, 0, gdal.GDT_Unknown)

    # field domain + vector layer with alias/comment
    dom = ogr.CreateCodedFieldDomain(prefix + "code_domain", "borehole type",
                                     ogr.OFTInteger, ogr.OFSTNone,
                                     {1: "core", 2: "percussion"})
    ds.AddFieldDomain(dom)
    pts = ds.CreateLayer(prefix + "boreholes", srs, ogr.wkbPoint)
    fd = ogr.FieldDefn("name", ogr.OFTString)
    fd.SetAlternativeName("孔號")
    fd.SetComment("borehole id")
    pts.CreateField(fd)
    fd = ogr.FieldDefn("code", ogr.OFTInteger)
    fd.SetDomainName(prefix + "code_domain")
    pts.CreateField(fd)
    for i in range(3):
        f = ogr.Feature(pts.GetLayerDefn())
        f.SetField("name", "BH-%d" % (i + 1))
        f.SetField("code", 1 + i % 2)
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (%f %f)" % (x0 + 100 * i, y0 + 100)))
        pts.CreateFeature(f)
    pts.SetMetadataItem("DESCRIPTION", "GDAL layer description")

    logs = ds.CreateLayer(prefix + "logs", None, ogr.wkbNone)
    logs.CreateField(ogr.FieldDefn("bh_name", ogr.OFTString))
    logs.CreateField(ogr.FieldDefn("depth", ogr.OFTReal))
    for i in range(4):
        f = ogr.Feature(logs.GetLayerDefn())
        f.SetField("bh_name", "BH-%d" % (1 + i % 3))
        f.SetField("depth", 1.5 * i)
        logs.CreateFeature(f)

    rel = gdal.Relationship(prefix + "bh_logs", prefix + "boreholes", prefix + "logs",
                            gdal.GRC_ONE_TO_MANY)
    rel.SetLeftTableFields(["name"])
    rel.SetRightTableFields(["bh_name"])
    rel.SetRelatedTableType("features")
    ds.AddRelationship(rel)
    ds = None

    # RGB tiles + DEM
    mem = gdal.GetDriverByName("MEM").Create("", 64, 64, 3, gdal.GDT_Byte)
    mem.SetGeoTransform((x0, 5, 0, y0 + 320, 0, -5))
    mem.SetProjection(srs.ExportToWkt())
    for b in range(3):
        mem.GetRasterBand(b + 1).Fill(60 * (b + 1))
    gdal.Translate(path, mem, format="GPKG",
                   creationOptions=["APPEND_SUBDATASET=YES", "RASTER_TABLE=" + prefix + "ortho",
                                    "TILE_FORMAT=PNG"])
    dem = gdal.GetDriverByName("MEM").Create("", 32, 32, 1, gdal.GDT_Float32)
    dem.SetGeoTransform((x0, 10, 0, y0 + 320, 0, -10))
    dem.SetProjection(srs.ExportToWkt())
    dem.GetRasterBand(1).Fill(123.25)
    gdal.Translate(path, dem, format="GPKG",
                   creationOptions=["APPEND_SUBDATASET=YES", "RASTER_TABLE=" + prefix + "dem"])

    # plain (unregistered) table and a view
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE "%snotes" (id INTEGER PRIMARY KEY, txt TEXT)' % prefix)
    con.execute('INSERT INTO "%snotes" (txt) VALUES (\'hello\')' % prefix)
    con.execute('CREATE VIEW "%sv_core" AS SELECT fid, name FROM "%sboreholes" WHERE code = 1'
                % (prefix, prefix))
    con.commit()
    con.close()

    if with_qgis:
        _add_qgis_objects(path, prefix, project_name)
    return path


def _add_qgis_objects(path, prefix, project_name):
    from qgis.core import (QgsLayerMetadata, QgsProject, QgsProviderRegistry,
                           QgsRasterLayer, QgsVectorLayer)
    vl = QgsVectorLayer("{0}|layername={1}boreholes".format(path, prefix), "Boreholes", "ogr")
    assert vl.isValid()
    vl.renderer().symbol().setColor(__import__("qgis.PyQt.QtGui", fromlist=["QColor"]).QColor("#d81b60"))
    vl.saveStyleToDatabase("default", "style of " + prefix + "boreholes", True, "")
    md = QgsLayerMetadata()
    md.setTitle("QGIS metadata " + prefix + "boreholes")
    md.setAbstract("abstract")
    QgsProviderRegistry.instance().providerMetadata("ogr").saveLayerMetadata(vl.source(), md)

    rl = QgsRasterLayer("GPKG:{0}:{1}ortho".format(path, prefix), "Ortho", "gdal")
    assert rl.isValid()
    proj = QgsProject()
    proj.addMapLayer(vl)
    proj.addMapLayer(rl)
    ok = proj.write("geopackage:{0}?projectName={1}".format(path, project_name))
    assert ok, proj.error()
