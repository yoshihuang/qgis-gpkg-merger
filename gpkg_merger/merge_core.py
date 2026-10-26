# -*- coding: utf-8 -*-
"""GeoPackage merge engine (no Qt / QGIS dependency, only GDAL/OGR + sqlite3).

Everything stored in the input GeoPackages is merged:

* vector and attribute layers (GDAL VectorTranslate: keeps field aliases,
  comments, value domains, spatial index)
* raster tiles, 2D gridded coverages (DEM) and vector tiles
* plain SQLite tables and views
* QGIS layer styles, QGIS projects (layer sources are redirected to the
  output file) and metadata
* related-table relations

Workflow
--------
1. :func:`scan_gpkg` reads the objects of every input file.
2. :func:`build_plan` decides, for the chosen conflict mode, which layer of
   which file goes where in the output.  Nothing is written yet; if the plan
   contains errors (e.g. incompatible layers in *append* mode) the caller
   must stop and let the user change the selection.
3. :func:`execute_plan` writes the output GeoPackage (to a temporary file
   first, which is moved into place only when everything succeeded).

Conflict modes for objects with the same name in several files
(names are compared case-insensitively, as SQLite does; projects use the
same rules within their own name space):

* ``MODE_RENAME``    – keep all of them, renamed ``<gpkg name>_<layer name>``
* ``MODE_OVERWRITE`` – the layer of the file that comes later in the merge
                       order replaces the earlier ones
* ``MODE_APPEND``    – append the features into one layer; geometry type,
                       CRS and fields must match, otherwise the plan fails.
                       Objects that cannot be appended (rasters, tables,
                       views, projects) are kept with new names instead.
"""

import os
import pathlib
import re
import sqlite3
from contextlib import contextmanager

from osgeo import gdal, ogr, osr

from . import gpkg_extras as gx
from .i18n_util import tr
from .project_rewrite import SourceRewriter, rewrite_project

MODE_RENAME = "rename"
MODE_OVERWRITE = "overwrite"
MODE_APPEND = "append"
MODES = (MODE_RENAME, MODE_OVERWRITE, MODE_APPEND)

STYLE_TABLE = "layer_styles"
PROJECT_TABLE = "qgis_projects"

# kinds of objects
KIND_FEATURES = "features"
KIND_ATTRIBUTES = "attributes"
KIND_TILES = "tiles"            # tiles, 2d-gridded-coverage, vector-tiles …
KIND_TABLE = "table"            # SQLite table not registered in gpkg_contents
KIND_VIEW = "view"              # SQLite view not registered in gpkg_contents
VECTOR_KINDS = (KIND_FEATURES, KIND_ATTRIBUTES)


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
    """Any table-like object of a GeoPackage (layer, raster, table, view)."""

    def __init__(self, name, kind=KIND_FEATURES, data_type=""):
        self.name = name
        self.kind = kind
        self.data_type = data_type or kind
        self.geom_type = ogr.wkbNone
        self.srs_wkt = ""
        self.srs_name = ""
        self.fields = []
        self.feature_count = 0

    @property
    def is_vector(self):
        return self.kind in VECTOR_KINDS

    @property
    def geom_type_name(self):
        if self.kind == KIND_TILES:
            if self.data_type == "2d-gridded-coverage":
                return tr("Raster (gridded coverage)")
            if self.data_type == "vector-tiles":
                return tr("Vector tiles")
            return tr("Raster (tiles)")
        if self.kind == KIND_TABLE:
            return tr("Table (not registered)")
        if self.kind == KIND_VIEW:
            return tr("View")
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
        self.layers = []          # list[LayerInfo] – every object kind
        self.projects = []        # names of QGIS projects stored in the file
        self.ogr_order = []       # OGR layer order (for old "|layerid=N" sources)
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

    def __init__(self, source_index, src_layer, out_name, action, kind=KIND_FEATURES):
        self.source_index = source_index
        self.src_layer = src_layer
        self.out_name = out_name
        self.action = action
        self.kind = kind


class Plan(object):
    def __init__(self, sources, mode):
        self.sources = sources
        self.mode = mode
        self.steps = []
        self.errors = []      # blocking problems – nothing must be written
        self.notes = []       # informative messages
        # per source index: {source layer name: output layer name} for the
        # objects actually copied from that source (styles, metadata)
        self.style_maps = {}
        # per source index: {lower-case name: output name} for *every* object
        # of the source, including overwritten / appended ones (projects)
        self.table_maps = {}
        # QGIS projects: list of (source index, name, output name)
        self.project_steps = []

    @property
    def ok(self):
        return not self.errors

    @property
    def output_layers(self):
        return [s.out_name for s in self.steps if s.action == Step.CREATE]

    @property
    def output_objects(self):
        """[(output name, kind)] of everything created."""
        return [(s.out_name, s.kind) for s in self.steps if s.action == Step.CREATE]


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------
def _sqlite_ro(path):
    uri = pathlib.Path(os.path.abspath(path)).as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def scan_gpkg(path):
    """Read information about every object of a GeoPackage."""
    info = SourceInfo(path)
    with _gdal_exceptions():
        try:
            ds = gdal.OpenEx(path, gdal.OF_VECTOR | gdal.OF_READONLY, allowed_drivers=["GPKG"],
                             open_options=["LIST_ALL_TABLES=NO"])
        except RuntimeError as e:
            raise MergeError(tr("Cannot open GeoPackage: {0}").format(path) + "\n" + str(e))
        if ds is None:
            raise MergeError(tr("Cannot open GeoPackage: {0}").format(path))

        for i in range(ds.GetLayerCount()):
            lyr = ds.GetLayerByIndex(i)
            name = lyr.GetName()
            low = name.lower()
            if low == STYLE_TABLE:
                info.has_styles = True
                continue
            if low == PROJECT_TABLE:
                continue
            geom = lyr.GetGeomType()
            li = LayerInfo(name, KIND_FEATURES if geom != ogr.wkbNone else KIND_ATTRIBUTES)
            li.geom_type = geom
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

        # layer order as QGIS sees it (default open options)
        try:
            ds = gdal.OpenEx(path, gdal.OF_VECTOR | gdal.OF_READONLY, allowed_drivers=["GPKG"])
            info.ogr_order = [ds.GetLayerByIndex(i).GetName() for i in range(ds.GetLayerCount())]
            ds = None
        except RuntimeError:
            info.ogr_order = [lyr.name for lyr in info.layers]

    _scan_sqlite(path, info)
    return info


def _scan_sqlite(path, info):
    """Objects OGR does not report: rasters, plain tables, views, projects."""
    try:
        con = _sqlite_ro(path)
    except sqlite3.Error as e:
        raise MergeError(tr("Cannot open GeoPackage: {0}").format(path) + "\n" + str(e))
    try:
        known = {lyr.name.lower() for lyr in info.layers}
        registered = {}
        for name, dtype, srs_id in con.execute(
                "SELECT table_name, data_type, srs_id FROM gpkg_contents"):
            registered[name.lower()] = (name, dtype, srs_id)
        for low, (name, dtype, srs_id) in registered.items():
            if dtype in VECTOR_KINDS or low in known or low in (STYLE_TABLE, PROJECT_TABLE):
                continue
            li = LayerInfo(name, KIND_TILES, dtype)
            row = con.execute("SELECT organization, organization_coordsys_id, srs_name "
                              "FROM gpkg_spatial_ref_sys WHERE srs_id = ?", (srs_id,)).fetchone()
            if row:
                li.srs_name = ("{0}:{1}".format(row[0], row[1])
                               if row[0] and row[0].upper() != "NONE" else (row[2] or ""))
            try:
                li.feature_count = con.execute(
                    "SELECT count(*) FROM {0}".format(gx.q(name))).fetchone()[0]  # nosec B608
            except sqlite3.Error:
                li.feature_count = 0
            info.layers.append(li)

        for typ, name in con.execute(
                "SELECT type, name FROM sqlite_master WHERE type IN ('table', 'view') "
                "ORDER BY type DESC, rowid"):
            low = name.lower()
            if low in registered or low in known or gx.is_system_table(name):
                continue
            if typ == "table":
                li = LayerInfo(name, KIND_TABLE)
                try:
                    li.feature_count = con.execute(
                        "SELECT count(*) FROM {0}".format(gx.q(name))).fetchone()[0]  # nosec B608
                except sqlite3.Error:
                    li.feature_count = 0
            else:
                li = LayerInfo(name, KIND_VIEW)
                li.feature_count = None
            info.layers.append(li)

        if con.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' "
                       "AND lower(name) = ?", (PROJECT_TABLE,)).fetchone():
            info.projects = [r[0] for r in con.execute(
                "SELECT name FROM {0} ORDER BY name".format(PROJECT_TABLE))]  # nosec B608
    except sqlite3.Error as e:
        raise MergeError(tr("Cannot open GeoPackage: {0}").format(path) + "\n" + str(e))
    finally:
        con.close()


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
    object name used in more than one place."""
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
        plan.table_maps[si] = {}

    def _keep(si, lyr, out, action=Step.CREATE):
        plan.steps.append(Step(si, lyr.name, out, action, lyr.kind))
        plan.table_maps[si][lyr.name.lower()] = out
        if action == Step.CREATE:
            plan.style_maps[si][lyr.name] = out

    def fname(si):
        return os.path.basename(sources[si].path)

    # ordered groups by first appearance
    order, groups = [], {}
    for si, src in enumerate(sources):
        for lyr in src.layers:
            key = lyr.name.lower()
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append((si, lyr))

    # Reserve every name that will be kept unchanged first so generated
    # names never collide with them.
    used = set(k for k in order if len(groups[k]) == 1)

    # Duplicate file names (same name in different folders) get _2, _3 …
    stems, seen = [], set()
    for src in sources:
        stems.append(_unique(safe_name(src.stem), seen))

    def _rename_all(occ, why=None):
        for si, lyr in occ:
            new = _unique("{0}_{1}".format(stems[si], lyr.name), used)
            _keep(si, lyr, new)
            plan.notes.append(tr("Layer '{0}' of '{1}' renamed to '{2}'").format(
                lyr.name, fname(si), new) + (" – " + why if why else ""))

    for key in order:
        occ = groups[key]
        if len(occ) == 1:
            si, lyr = occ[0]
            _keep(si, lyr, lyr.name)
            continue

        if mode == MODE_RENAME:
            _rename_all(occ)

        elif mode == MODE_OVERWRITE:
            si, lyr = occ[-1]
            _keep(si, lyr, lyr.name)
            for osi, olyr in occ[:-1]:
                plan.table_maps[osi][olyr.name.lower()] = lyr.name
                plan.notes.append(tr("Layer '{0}' of '{1}' is overwritten by '{2}'").format(
                    olyr.name, fname(osi), fname(si)))

        elif not all(lyr.is_vector for _si, lyr in occ):
            # rasters, tables, views cannot be appended – keep them all
            _rename_all(occ, tr("only vector and attribute layers can be appended"))

        else:  # MODE_APPEND
            si0, base = occ[0]
            _keep(si0, base, base.name)
            for si, lyr in occ[1:]:
                problems = check_compatible(base, lyr)
                if problems:
                    plan.errors.append(
                        tr("Layer '{0}': '{1}' cannot be appended to '{2}': {3}").format(
                            base.name, fname(si), fname(si0), "; ".join(problems)))
                else:
                    _keep(si, lyr, base.name, Step.APPEND)
                    plan.notes.append(tr("{0} features of '{1}' in '{2}' appended to layer '{3}'").format(
                        lyr.feature_count, lyr.name, fname(si), base.name))

    # QGIS projects (own name space)
    p_order, p_groups = [], {}
    for si, src in enumerate(sources):
        for name in src.projects:
            key = name.lower()
            if key not in p_groups:
                p_groups[key] = []
                p_order.append(key)
            p_groups[key].append((si, name))
    p_used = set(k for k in p_order if len(p_groups[k]) == 1)
    for key in p_order:
        occ = p_groups[key]
        if len(occ) == 1:
            plan.project_steps.append((occ[0][0], occ[0][1], occ[0][1]))
        elif mode == MODE_OVERWRITE:
            si, name = occ[-1]
            plan.project_steps.append((si, name, name))
            for osi, oname in occ[:-1]:
                plan.notes.append(tr("Project '{0}' of '{1}' is overwritten by '{2}'").format(
                    oname, fname(osi), fname(si)))
        else:
            for si, name in occ:
                new = _unique("{0}_{1}".format(stems[si], name), p_used)
                plan.project_steps.append((si, name, new))
                plan.notes.append(tr("Project '{0}' of '{1}' renamed to '{2}'").format(
                    name, fname(si), new))

    for src in sources:
        for name, reason in src.skipped:
            plan.notes.append(tr("Skipped '{0}' in '{1}': {2}").format(
                name, os.path.basename(src.path), reason))
    return plan


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------
def execute_plan(plan, output_path, copy_styles=True, progress=None, log=None):
    """Write the output GeoPackage.

    progress(fraction 0..1) -> bool : return False to cancel
    log(message)
    Returns [(output name, kind)] of the created objects.
    """
    if not plan.ok:
        raise MergeError(tr("The merge plan contains errors; nothing was written."))
    if not plan.steps and not plan.project_steps:
        raise MergeError(tr("There is nothing to merge."))

    out_abs = os.path.normcase(os.path.abspath(output_path))
    for src in plan.sources:
        if os.path.normcase(os.path.abspath(src.path)) == out_abs:
            raise MergeError(tr("The output file must not be one of the input files."))

    log = log or (lambda msg: None)
    tmp_path = output_path + ".partial.gpkg"
    _cleanup(tmp_path)

    vector_steps = [s for s in plan.steps if s.kind in VECTOR_KINDS]
    style_jobs = []
    if copy_styles:
        for si, src in enumerate(plan.sources):
            if src.has_styles and plan.style_maps.get(si):
                style_jobs.append(si)
    total = len(vector_steps) + len(style_jobs) + len(plan.sources) + 1
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
            # 1. vector / attribute layers with OGR
            for step in vector_steps:
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
                _translate(tmp_path, src.path, opts)  # dataset closed when released
                created = True
                state["done"] += 1

            if not created:  # only rasters / tables / projects
                gdal.GetDriverByName("GPKG").Create(tmp_path, 0, 0, 0, gdal.GDT_Unknown).FlushCache()

            # 2. QGIS layer styles
            for si in style_jobs:
                _check_cancel()
                src = plan.sources[si]
                log(tr("Copying layer styles from '{0}'").format(os.path.basename(src.path)))
                _copy_styles(src.path, tmp_path, plan.style_maps[si])
                state["done"] += 1

        # 3. everything else, directly with SQLite
        _copy_raw(plan, tmp_path, output_path, log, _check_cancel, state)

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
    return plan.output_objects


def _copy_raw(plan, tmp_path, output_path, log, check_cancel, state):
    con = sqlite3.connect(tmp_path, isolation_level=None)
    try:
        con.execute("PRAGMA foreign_keys = OFF")
        srs = gx.SrsMapper(con)
        md_maps = {}
        views = []   # created last, when all tables exist
        for si, src in enumerate(plan.sources):
            check_cancel()
            steps = [s for s in plan.steps if s.source_index == si and s.action == Step.CREATE]
            mapping = dict(plan.table_maps[si])
            kept = {s.src_layer.lower() for s in steps}
            con.execute("ATTACH DATABASE ? AS src",
                        (pathlib.Path(os.path.abspath(src.path)).as_uri() + "?mode=ro",))
            srs.reset()
            md_maps[si] = {}
            try:
                con.execute("BEGIN")
                for step in steps:
                    if step.kind == KIND_TILES:
                        log(tr("Copying raster '{0}' from '{1}' as '{2}'").format(
                            step.src_layer, os.path.basename(src.path), step.out_name))
                        failed = gx.copy_tile_object(con, step.src_layer, step.out_name,
                                                     srs, mapping)
                    elif step.kind == KIND_TABLE:
                        log(tr("Copying table '{0}' from '{1}' as '{2}'").format(
                            step.src_layer, os.path.basename(src.path), step.out_name))
                        failed = gx.copy_plain_table(con, step.src_layer, step.out_name,
                                                     mapping)
                    else:
                        failed = []
                        if step.kind == KIND_VIEW:
                            views.append((si, step))
                    for msg in failed or []:
                        log(tr("Index or trigger skipped: {0}").format(msg))
                    if step.kind != KIND_VIEW:
                        gx.copy_metadata(con, step.src_layer, step.out_name,
                                         skip_gdal=step.kind in VECTOR_KINDS, id_map=md_maps[si])
                gx.copy_geopackage_metadata(con, md_maps[si])
                if gx.copy_relations(con, mapping, kept):
                    log(tr("Copying relations from '{0}'").format(os.path.basename(src.path)))
                gx.copy_system_extensions(con)
                _copy_projects(con, plan, si, output_path, log)
                con.execute("COMMIT")
            except Exception:
                if con.in_transaction:
                    con.execute("ROLLBACK")
                raise
            finally:
                con.execute("DETACH DATABASE src")
            state["done"] += 1

        for si, step in views:
            src = plan.sources[si]
            con.execute("ATTACH DATABASE ? AS src",
                        (pathlib.Path(os.path.abspath(src.path)).as_uri() + "?mode=ro",))
            try:
                err = gx.create_view(con, step.src_layer, step.out_name, plan.table_maps[si])
            finally:
                con.execute("DETACH DATABASE src")
            if err:
                log(tr("View '{0}' of '{1}' could not be re-created and was skipped: {2}").format(
                    step.src_layer, os.path.basename(src.path), err))
            else:
                log(tr("Copying view '{0}' from '{1}' as '{2}'").format(
                    step.src_layer, os.path.basename(src.path), step.out_name))
        state["done"] += 1
    finally:
        con.close()


def _copy_projects(con, plan, si, output_path, log):
    steps = [(name, out) for psi, name, out in plan.project_steps if psi == si]
    if not steps:
        return
    if not gx.has_table(con, "main", PROJECT_TABLE):
        con.execute("CREATE TABLE qgis_projects (name TEXT PRIMARY KEY, metadata BLOB, "
                    "content BLOB)")
    rewriter = SourceRewriter(
        [{"path": s.path, "tables": plan.table_maps[i], "ogr_order": s.ogr_order}
         for i, s in enumerate(plan.sources)], output_path)
    base_dir = os.path.dirname(os.path.abspath(plan.sources[si].path))
    for name, out in steps:
        row = con.execute("SELECT metadata, content FROM src.{0} WHERE name = ?".format(  # nosec B608
            PROJECT_TABLE), (name,)).fetchone()
        if row is None:
            continue
        content = rewrite_project(row[1], rewriter, base_dir)
        con.execute("DELETE FROM main.{0} WHERE name = ?".format(PROJECT_TABLE), (out,))  # nosec B608
        con.execute("INSERT INTO main.{0} (name, metadata, content) VALUES (?, ?, ?)".format(  # nosec B608
            PROJECT_TABLE), (out, row[0], content))
        log(tr("Copying QGIS project '{0}' from '{1}' as '{2}'").format(
            name, os.path.basename(plan.sources[si].path), out))


# Columns QGIS reads/writes in layer_styles (older files may lack some).
_STYLE_COLUMNS = [
    ("f_table_catalog", ogr.OFTString, ogr.OFSTNone),
    ("f_table_schema", ogr.OFTString, ogr.OFSTNone),
    ("f_table_name", ogr.OFTString, ogr.OFSTNone), ("f_geometry_column", ogr.OFTString, ogr.OFSTNone),
    ("styleName", ogr.OFTString, ogr.OFSTNone), ("styleQML", ogr.OFTString, ogr.OFSTNone),
    ("styleSLD", ogr.OFTString, ogr.OFSTNone), ("useAsDefault", ogr.OFTInteger, ogr.OFSTBoolean),
    ("description", ogr.OFTString, ogr.OFSTNone), ("owner", ogr.OFTString, ogr.OFSTNone),
    ("ui", ogr.OFTString, ogr.OFSTNone), ("update_time", ogr.OFTDateTime, ogr.OFSTNone),
]


def _copy_styles(src_path, dst_path, mapping):
    """Copy the layer_styles rows of the mapped layers with the OGR feature
    API (no SQL), writing the output layer name into f_table_name."""
    src_ds = gdal.OpenEx(src_path, gdal.OF_VECTOR | gdal.OF_READONLY)
    s_lyr = src_ds.GetLayerByName(STYLE_TABLE)
    s_defn = s_lyr.GetLayerDefn()
    if s_defn.GetFieldIndex("f_table_name") < 0:
        return
    dst_ds = gdal.OpenEx(dst_path, gdal.OF_VECTOR | gdal.OF_UPDATE)
    d_lyr = dst_ds.GetLayerByName(STYLE_TABLE)
    if d_lyr is None:
        d_lyr = dst_ds.CreateLayer(STYLE_TABLE, None, ogr.wkbNone, ["FID=id"])
        for name, ftype, subtype in _STYLE_COLUMNS:
            fd = ogr.FieldDefn(name, ftype)
            fd.SetSubType(subtype)
            d_lyr.CreateField(fd)
    d_defn = d_lyr.GetLayerDefn()
    have = {d_defn.GetFieldDefn(i).GetName().lower() for i in range(d_defn.GetFieldCount())}
    for i in range(s_defn.GetFieldCount()):  # columns of newer QGIS versions
        fd = s_defn.GetFieldDefn(i)
        if fd.GetName().lower() not in have:
            d_lyr.CreateField(fd)
    d_defn = d_lyr.GetLayerDefn()

    dst_ds.StartTransaction()
    for feat in s_lyr:
        table = feat.GetField("f_table_name")
        if table not in mapping:
            continue
        out = ogr.Feature(d_defn)
        out.SetFrom(feat)          # fields are matched by name
        out.SetFID(ogr.NullFID)
        out.SetField("f_table_name", mapping[table])
        d_lyr.CreateFeature(out)
    dst_ds.CommitTransaction()
    dst_ds = None
    src_ds = None


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
