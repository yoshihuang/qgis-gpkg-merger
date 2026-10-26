# -*- coding: utf-8 -*-
"""GeoPackage merge engine (no Qt / QGIS dependency, only GDAL/OGR).

Workflow
--------
1. :func:`scan_gpkg` reads the layers of every input file.
2. :func:`build_plan` decides, for the chosen conflict mode, which layer of
   which file goes where in the output.  Nothing is written yet; if the plan
   contains errors (e.g. incompatible layers in *append* mode) the caller
   must stop and let the user change the selection.
3. :func:`execute_plan` writes the output GeoPackage (to a temporary file
   first, which is moved into place only when everything succeeded).

Conflict modes for layers with the same name in several files
(names are compared case-insensitively, as SQLite does):

* ``MODE_RENAME``    – keep all of them, renamed ``<gpkg name>_<layer name>``
* ``MODE_OVERWRITE`` – the layer of the file that comes later in the merge
                       order replaces the earlier ones
* ``MODE_APPEND``    – append the features into one layer; geometry type,
                       CRS and fields must match, otherwise the plan fails
"""

import os
import re
from contextlib import contextmanager

from osgeo import gdal, ogr, osr

from .i18n_util import tr

MODE_RENAME = "rename"
MODE_OVERWRITE = "overwrite"
MODE_APPEND = "append"
MODES = (MODE_RENAME, MODE_OVERWRITE, MODE_APPEND)

STYLE_TABLE = "layer_styles"
# Tables that are not data layers and are handled separately / skipped.
_SPECIAL_TABLES = {STYLE_TABLE, "qgis_projects"}


class MergeError(Exception):
    """Raised for failures while writing the output."""


class MergeCancelled(Exception):
    """Raised when the user cancels the merge."""


@contextmanager
def _gdal_exceptions():
    """Enable GDAL exceptions locally without changing global state for
    other QGIS plugins."""
    if hasattr(gdal, "ExceptionMgr"):
        with gdal.ExceptionMgr(useExceptions=True), ogr.ExceptionMgr(useExceptions=True), \
                osr.ExceptionMgr(useExceptions=True):
            yield
        return
    old = (gdal.GetUseExceptions(), ogr.GetUseExceptions(), osr.GetUseExceptions())
    gdal.UseExceptions()
    ogr.UseExceptions()
    osr.UseExceptions()
    try:
        yield
    finally:
        if not old[0]:
            gdal.DontUseExceptions()
        if not old[1]:
            ogr.DontUseExceptions()
        if not old[2]:
            osr.DontUseExceptions()


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
class FieldInfo(object):
    __slots__ = ("name", "type", "subtype")

    def __init__(self, name, ftype, subtype):
        self.name = name
        self.type = ftype
        self.subtype = subtype

    @property
    def type_name(self):
        name = ogr.GetFieldTypeName(self.type)
        if self.subtype:
            name += "(" + ogr.GetFieldSubTypeName(self.subtype) + ")"
        return name


class LayerInfo(object):
    def __init__(self, name):
        self.name = name
        self.geom_type = ogr.wkbNone
        self.srs_wkt = ""
        self.srs_name = ""
        self.fields = []
        self.feature_count = 0

    @property
    def geom_type_name(self):
        if self.geom_type == ogr.wkbNone:
            return tr("No geometry")
        return ogr.GeometryTypeToName(self.geom_type)

    def srs(self):
        if not self.srs_wkt:
            return None
        s = osr.SpatialReference()
        s.ImportFromWkt(self.srs_wkt)
        return s


class SourceInfo(object):
    def __init__(self, path):
        self.path = path
        self.stem = os.path.splitext(os.path.basename(path))[0]
        self.layers = []          # list[LayerInfo]
        self.has_styles = False   # contains a QGIS layer_styles table
        self.skipped = []         # list[(table name, reason)]

    def layer(self, name):
        for lyr in self.layers:
            if lyr.name == name:
                return lyr
        return None


class Step(object):
    """One copy operation: a source layer into an output layer."""
    CREATE = "create"
    APPEND = "append"

    def __init__(self, source_index, src_layer, out_name, action):
        self.source_index = source_index
        self.src_layer = src_layer
        self.out_name = out_name
        self.action = action


class Plan(object):
    def __init__(self, sources, mode):
        self.sources = sources
        self.mode = mode
        self.steps = []
        self.errors = []      # blocking problems – nothing must be written
        self.notes = []       # informative messages
        # per source index: {source layer name: output layer name}
        self.style_maps = {}

    @property
    def ok(self):
        return not self.errors

    @property
    def output_layers(self):
        return [s.out_name for s in self.steps if s.action == Step.CREATE]


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------
def scan_gpkg(path):
    """Read layer information of a GeoPackage."""
    info = SourceInfo(path)
    with _gdal_exceptions():
        try:
            ds = gdal.OpenEx(path, gdal.OF_VECTOR | gdal.OF_READONLY, allowed_drivers=["GPKG"])
        except RuntimeError as e:
            raise MergeError(tr("Cannot open GeoPackage: {0}").format(path) + "\n" + str(e))
        if ds is None:
            raise MergeError(tr("Cannot open GeoPackage: {0}").format(path))

        # Raster / tile tables are not handled by this plugin.
        try:
            sql = ds.ExecuteSQL(
                "SELECT table_name, data_type FROM gpkg_contents "
                "WHERE data_type NOT IN ('features', 'attributes')")
            if sql is not None:
                for f in sql:
                    info.skipped.append((f.GetField(0), tr("raster/tiles table is not supported")))
                ds.ReleaseResultSet(sql)
        except RuntimeError:
            pass

        for i in range(ds.GetLayerCount()):
            lyr = ds.GetLayerByIndex(i)
            name = lyr.GetName()
            low = name.lower()
            if low == STYLE_TABLE:
                info.has_styles = True
                continue
            if low in _SPECIAL_TABLES:
                info.skipped.append((name, tr("QGIS project storage table is not merged")))
                continue
            li = LayerInfo(name)
            li.geom_type = lyr.GetGeomType()
            srs = lyr.GetSpatialRef()
            if srs is not None:
                li.srs_wkt = srs.ExportToWkt()
                auth = srs.GetAuthorityName(None)
                code = srs.GetAuthorityCode(None)
                li.srs_name = "{0}:{1}".format(auth, code) if auth and code else (srs.GetName() or "")
            defn = lyr.GetLayerDefn()
            for j in range(defn.GetFieldCount()):
                fd = defn.GetFieldDefn(j)
                li.fields.append(FieldInfo(fd.GetName(), fd.GetType(), fd.GetSubType()))
            li.feature_count = lyr.GetFeatureCount()
            info.layers.append(li)
        ds = None
    return info


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------
_BAD_CHARS = re.compile(r"[^\w]+", re.UNICODE)


def safe_name(text):
    """Make a table-name friendly string (keeps Unicode letters, e.g. CJK)."""
    out = _BAD_CHARS.sub("_", text).strip("_")
    return out or "layer"


def _unique(name, used):
    """Return *name* or name_2, name_3 ... not yet in *used* (lower-case set)."""
    candidate = name
    n = 2
    while candidate.lower() in used:
        candidate = "{0}_{1}".format(name, n)
        n += 1
    used.add(candidate.lower())
    return candidate


def check_compatible(target, other):
    """Return a list of human readable reasons why *other* cannot be
    appended to *target* (empty list = compatible)."""
    problems = []
    if target.geom_type != other.geom_type and target.geom_type != ogr.wkbUnknown:
        problems.append(tr("geometry type differs ({0} vs {1})").format(
            target.geom_type_name, other.geom_type_name))

    s1, s2 = target.srs(), other.srs()
    if (s1 is None) != (s2 is None):
        problems.append(tr("coordinate reference system differs ({0} vs {1})").format(
            target.srs_name or tr("none"), other.srs_name or tr("none")))
    elif s1 is not None and not s1.IsSame(s2):
        problems.append(tr("coordinate reference system differs ({0} vs {1})").format(
            target.srs_name, other.srs_name))

    f1 = {f.name.lower(): f for f in target.fields}
    f2 = {f.name.lower(): f for f in other.fields}
    missing = [f1[k].name for k in f1 if k not in f2]
    extra = [f2[k].name for k in f2 if k not in f1]
    if missing:
        problems.append(tr("missing fields: {0}").format(", ".join(missing)))
    if extra:
        problems.append(tr("extra fields: {0}").format(", ".join(extra)))
    for k in f1:
        if k in f2 and (f1[k].type, f1[k].subtype) != (f2[k].type, f2[k].subtype):
            problems.append(tr("field '{0}' type differs ({1} vs {2})").format(
                f1[k].name, f1[k].type_name, f2[k].type_name))
    return problems


def find_conflicts(sources):
    """Return {lower-case name: [(source index, LayerInfo), ...]} for every
    layer name used in more than one place."""
    groups = {}
    for si, src in enumerate(sources):
        for lyr in src.layers:
            groups.setdefault(lyr.name.lower(), []).append((si, lyr))
    return {k: v for k, v in groups.items() if len(v) > 1}


def build_plan(sources, mode):
    """Decide what to copy where.  *sources* is the ordered list of
    :class:`SourceInfo` (first = merged first)."""
    if mode not in MODES:
        raise ValueError(mode)
    plan = Plan(sources, mode)
    for si in range(len(sources)):
        plan.style_maps[si] = {}

    # ordered groups by first appearance
    order, groups = [], {}
    for si, src in enumerate(sources):
        for lyr in src.layers:
            key = lyr.name.lower()
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append((si, lyr))

    # Rename mode: reserve every name that will be kept unchanged first so
    # generated names never collide with them.
    used = set(k for k in order if len(groups[k]) == 1)

    # Duplicate file names (same name in different folders) get _2, _3 …
    stems, seen = [], set()
    for src in sources:
        stems.append(_unique(safe_name(src.stem), seen))

    for key in order:
        occ = groups[key]
        if len(occ) == 1:
            si, lyr = occ[0]
            plan.steps.append(Step(si, lyr.name, lyr.name, Step.CREATE))
            plan.style_maps[si][lyr.name] = lyr.name
            continue

        if mode == MODE_RENAME:
            for si, lyr in occ:
                new = _unique("{0}_{1}".format(stems[si], lyr.name), used)
                plan.steps.append(Step(si, lyr.name, new, Step.CREATE))
                plan.style_maps[si][lyr.name] = new
                plan.notes.append(tr("Layer '{0}' of '{1}' renamed to '{2}'").format(
                    lyr.name, os.path.basename(sources[si].path), new))

        elif mode == MODE_OVERWRITE:
            si, lyr = occ[-1]
            plan.steps.append(Step(si, lyr.name, lyr.name, Step.CREATE))
            plan.style_maps[si][lyr.name] = lyr.name
            for osi, olyr in occ[:-1]:
                plan.notes.append(tr("Layer '{0}' of '{1}' is overwritten by '{2}'").format(
                    olyr.name, os.path.basename(sources[osi].path),
                    os.path.basename(sources[si].path)))

        else:  # MODE_APPEND
            si0, base = occ[0]
            plan.steps.append(Step(si0, base.name, base.name, Step.CREATE))
            plan.style_maps[si0][base.name] = base.name
            for si, lyr in occ[1:]:
                problems = check_compatible(base, lyr)
                if problems:
                    plan.errors.append(
                        tr("Layer '{0}': '{1}' cannot be appended to '{2}': {3}").format(
                            base.name, os.path.basename(sources[si].path),
                            os.path.basename(sources[si0].path), "; ".join(problems)))
                else:
                    plan.steps.append(Step(si, lyr.name, base.name, Step.APPEND))
                    plan.notes.append(tr("{0} features of '{1}' in '{2}' appended to layer '{3}'").format(
                        lyr.feature_count, lyr.name, os.path.basename(sources[si].path), base.name))

    for src in sources:
        for name, reason in src.skipped:
            plan.notes.append(tr("Skipped '{0}' in '{1}': {2}").format(
                name, os.path.basename(src.path), reason))
    return plan


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------
def _sql_str(text):
    return "'" + text.replace("'", "''") + "'"


def _sql_ident(text):
    return '"' + text.replace('"', '""') + '"'


def _style_sql(src_ds, mapping):
    """SELECT statement copying the style rows of the mapped layers, with
    f_table_name replaced by the output layer name."""
    lyr = src_ds.GetLayerByName(STYLE_TABLE)
    defn = lyr.GetLayerDefn()
    cols = []
    has_table_col = False
    for i in range(defn.GetFieldCount()):
        name = defn.GetFieldDefn(i).GetName()
        if name.lower() == "f_table_name":
            has_table_col = True
            case = "CASE " + " ".join(
                "WHEN f_table_name = {0} THEN {1}".format(_sql_str(k), _sql_str(v))
                for k, v in mapping.items()) + " END AS f_table_name"
            cols.append(case)
        else:
            cols.append(_sql_ident(name))
    if not has_table_col:
        return None
    return "SELECT {0} FROM {1} WHERE f_table_name IN ({2})".format(
        ", ".join(cols), STYLE_TABLE, ", ".join(_sql_str(k) for k in mapping))


def execute_plan(plan, output_path, copy_styles=True, progress=None, log=None):
    """Write the output GeoPackage.

    progress(fraction 0..1) -> bool : return False to cancel
    log(message)
    """
    if not plan.ok:
        raise MergeError(tr("The merge plan contains errors; nothing was written."))
    if not plan.steps:
        raise MergeError(tr("There is nothing to merge."))

    out_abs = os.path.normcase(os.path.abspath(output_path))
    for src in plan.sources:
        if os.path.normcase(os.path.abspath(src.path)) == out_abs:
            raise MergeError(tr("The output file must not be one of the input files."))

    log = log or (lambda msg: None)
    tmp_path = output_path + ".partial.gpkg"
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    style_jobs = []
    if copy_styles:
        for si, src in enumerate(plan.sources):
            if src.has_styles and plan.style_maps.get(si):
                style_jobs.append(si)
    total = len(plan.steps) + len(style_jobs)
    state = {"done": 0, "cancelled": False}

    def _cb(pct, _msg, _data):
        if progress is None:
            return 1
        frac = (state["done"] + max(0.0, min(1.0, pct))) / float(total)
        if progress(frac) is False:
            state["cancelled"] = True
            return 0
        return 1

    def _check_cancel():
        if state["cancelled"] or (progress is not None and
                                  progress(state["done"] / float(total)) is False):
            state["cancelled"] = True
            raise MergeCancelled()

    created = False
    try:
        with _gdal_exceptions():
            for step in plan.steps:
                _check_cancel()
                src = plan.sources[step.source_index]
                if step.action == Step.CREATE:
                    log(tr("Copying '{0}' from '{1}' as '{2}'").format(
                        step.src_layer, os.path.basename(src.path), step.out_name))
                    opts = gdal.VectorTranslateOptions(
                        format="GPKG",
                        layers=[step.src_layer],
                        layerName=step.out_name,
                        accessMode="update" if created else None,
                        options=["-preserve_fid"],
                        callback=_cb,
                    )
                else:
                    log(tr("Appending '{0}' from '{1}' to '{2}'").format(
                        step.src_layer, os.path.basename(src.path), step.out_name))
                    opts = gdal.VectorTranslateOptions(
                        format="GPKG",
                        layers=[step.src_layer],
                        layerName=step.out_name,
                        accessMode="append",
                        callback=_cb,
                    )
                ds = _translate(tmp_path, src.path, opts)
                ds = None
                created = True
                state["done"] += 1

            styles_created = False
            for si in style_jobs:
                _check_cancel()
                src = plan.sources[si]
                src_ds = gdal.OpenEx(src.path, gdal.OF_VECTOR | gdal.OF_READONLY)
                sql = _style_sql(src_ds, plan.style_maps[si])
                fid_name = src_ds.GetLayerByName(STYLE_TABLE).GetFIDColumn() or "id"
                src_ds = None
                if sql:
                    log(tr("Copying layer styles from '{0}'").format(os.path.basename(src.path)))
                    opts = gdal.VectorTranslateOptions(
                        format="GPKG",
                        SQLStatement=sql,
                        layerName=STYLE_TABLE,
                        accessMode="append" if styles_created else "update",
                        layerCreationOptions=None if styles_created else ["FID=" + fid_name],
                        callback=_cb,
                    )
                    ds = _translate(tmp_path, src.path, opts)
                    ds = None
                    styles_created = True
                state["done"] += 1
            if styles_created:
                _ensure_style_columns(tmp_path)

        if os.path.exists(output_path):
            os.remove(output_path)
        os.replace(tmp_path, output_path)
    except MergeCancelled:
        _cleanup(tmp_path)
        raise
    except Exception as e:
        _cleanup(tmp_path)
        if state["cancelled"]:
            raise MergeCancelled()
        if isinstance(e, MergeError):
            raise
        raise MergeError(str(e))

    if progress:
        progress(1.0)
    log(tr("Done: {0}").format(output_path))
    return plan.output_layers


# Columns QGIS reads/writes in layer_styles (older files may lack some).
_STYLE_COLUMNS = [
    ("f_table_catalog", ogr.OFTString), ("f_table_schema", ogr.OFTString),
    ("f_table_name", ogr.OFTString), ("f_geometry_column", ogr.OFTString),
    ("styleName", ogr.OFTString), ("styleQML", ogr.OFTString),
    ("styleSLD", ogr.OFTString), ("useAsDefault", ogr.OFTInteger),
    ("description", ogr.OFTString), ("owner", ogr.OFTString),
    ("ui", ogr.OFTString), ("update_time", ogr.OFTDateTime),
]


def _ensure_style_columns(path):
    ds = gdal.OpenEx(path, gdal.OF_VECTOR | gdal.OF_UPDATE)
    lyr = ds.GetLayerByName(STYLE_TABLE)
    defn = lyr.GetLayerDefn()
    have = {defn.GetFieldDefn(i).GetName().lower() for i in range(defn.GetFieldCount())}
    for name, ftype in _STYLE_COLUMNS:
        if name.lower() not in have:
            lyr.CreateField(ogr.FieldDefn(name, ftype))
    ds = None


def _translate(dst, src, opts):
    try:
        ds = gdal.VectorTranslate(dst, src, options=opts)
    except RuntimeError as e:
        if "user terminated" in str(e).lower() or "interrupted" in str(e).lower():
            raise MergeCancelled()
        raise
    if ds is None:
        raise MergeCancelled()
    return ds


def _cleanup(path):
    for p in (path, path + "-wal", path + "-shm", path + "-journal"):
        try:
            if os.path.exists(p):
                os.remove(p)
        except OSError:
            pass
