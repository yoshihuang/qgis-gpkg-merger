# -*- coding: utf-8 -*-
"""Raw SQLite copying of GeoPackage content that OGR does not carry over.

Vector and attribute layers are copied with GDAL's VectorTranslate (see
merge_core).  Everything else is copied here, table by table, from the
attached source database (schema ``src``) into the output (``main``):

* tile pyramids, 2D gridded coverages (DEM) and vector tiles, with their
  tile matrix (set), ancillary rows, extensions and spatial reference systems
* plain SQLite tables that are not registered in gpkg_contents (+ indexes,
  triggers) and views (table names in the view SQL are rewritten)
* gpkg_metadata / gpkg_metadata_reference (e.g. QGIS layer metadata)
* related-tables relations (gpkgext_relations)

Table and column names cannot be bound as SQL parameters, so they are always
quoted with :func:`q`; every *value* is passed as a bound parameter.
"""

import re

GDAL_MD_URI = "http://gdal.org"
SYSTEM_PREFIXES = ("gpkg_", "gpkgext_", "rtree_", "sqlite_")
SYSTEM_TABLES = {"layer_styles", "qgis_projects", "ogr_empty_table"}


def q(name):
    """Quote an SQLite identifier."""
    return '"' + str(name).replace('"', '""') + '"'


def is_system_table(name):
    low = name.lower()
    return low.startswith(SYSTEM_PREFIXES) or low in SYSTEM_TABLES


# ---------------------------------------------------------------------------
# generic helpers
# ---------------------------------------------------------------------------
def has_table(con, schema, name):
    row = con.execute(
        "SELECT 1 FROM {0}.sqlite_master WHERE type IN ('table','view') "  # nosec B608
        "AND lower(name) = lower(?)".format(schema), (name,)).fetchone()
    return row is not None


def columns(con, schema, table):
    return [r[1] for r in con.execute(
        "PRAGMA {0}.table_info({1})".format(schema, q(table)))]


def _master_sql(con, name, types=("table",)):
    marks = ",".join("?" for _ in types)
    row = con.execute(
        "SELECT sql FROM src.sqlite_master WHERE type IN ({0}) "  # nosec B608
        "AND lower(name) = lower(?)".format(marks), tuple(types) + (name,)).fetchone()
    return row[0] if row else None


_HEADER = re.compile(
    r'^\s*CREATE\s+(TABLE|VIEW)\s+(?:IF\s+NOT\s+EXISTS\s+)?'
    r'(?:"(?:[^"]|"")*"|\[[^\]]*\]|`[^`]*`|\'[^\']*\'|[^\s(]+)',
    re.IGNORECASE)


def _rename_header(sql, new_name):
    m = _HEADER.match(sql)
    if not m:
        raise ValueError("cannot parse: " + sql[:80])
    return "CREATE {0} {1}".format(m.group(1).upper(), q(new_name)) + sql[m.end():]


def rename_identifiers(sql, mapping):
    """Replace table names in an SQL statement (quoted or bare words)."""
    for old, new in mapping.items():
        if old.lower() == new.lower() and old == new:
            continue
        esc = re.escape(old)
        sql = re.sub(r'"' + esc + r'"', q(new), sql, flags=re.IGNORECASE)
        sql = re.sub(r'\[' + esc + r'\]', q(new), sql, flags=re.IGNORECASE)
        sql = re.sub(r'`' + esc + r'`', q(new), sql, flags=re.IGNORECASE)
        sql = re.sub(r'(?<![\w"\[`.])' + esc + r'(?![\w"\]`])', q(new), sql,
                     flags=re.IGNORECASE | re.UNICODE)
    return sql


def ensure_table_like(con, name):
    """Create table *name* in main with the source definition if missing."""
    if has_table(con, "main", name):
        return False
    sql = _master_sql(con, name)
    if not sql:
        return False
    con.execute(sql)
    return True


def copy_rows(con, src_table, out_table, overrides=None, skip=()):
    """INSERT INTO main.out SELECT ... FROM src.src_table, matching columns by
    name.  *overrides* maps column -> constant value (bound parameter)."""
    overrides = overrides or {}
    out_cols = {c.lower(): c for c in columns(con, "main", out_table)}
    src_cols = [c for c in columns(con, "src", src_table)
                if c.lower() in out_cols and c.lower() not in {s.lower() for s in skip}]
    sel, params = [], []
    for c in src_cols:
        if c.lower() in {k.lower() for k in overrides}:
            sel.append("?")
            params.append([v for k, v in overrides.items() if k.lower() == c.lower()][0])
        else:
            sel.append(q(c))
    if not src_cols:
        return 0
    return con.execute(
        "INSERT INTO main.{0} ({1}) SELECT {2} FROM src.{3}".format(  # nosec B608
            q(out_table), ", ".join(q(out_cols[c.lower()]) for c in src_cols),
            ", ".join(sel), q(src_table)), params).rowcount


def _insert_row(con, table, row):
    """Insert a dict into main.table, keeping only columns that exist."""
    cols = {c.lower(): c for c in columns(con, "main", table)}
    keys = [k for k in row if k.lower() in cols]
    con.execute("INSERT INTO main.{0} ({1}) VALUES ({2})".format(  # nosec B608
        q(table), ", ".join(q(cols[k.lower()]) for k in keys),
        ", ".join("?" for _ in keys)), [row[k] for k in keys])


def _rows(con, sql, params=()):
    cur = con.execute(sql, params)
    names = [d[0] for d in cur.description]
    return [dict(zip(names, r)) for r in cur.fetchall()]


def _copy_dependents(con, src_table, out_table, mapping):
    """Copy indexes and triggers that belong to src_table.  These are
    optional, so a failure is reported but does not stop the merge."""
    failed = []
    for row in _rows(con, "SELECT type, name, sql FROM src.sqlite_master "
                          "WHERE type IN ('index','trigger') AND sql IS NOT NULL "
                          "AND lower(tbl_name) = lower(?)", (src_table,)):
        sql = rename_identifiers(row["sql"], mapping)
        new_name = row["name"]
        if src_table.lower() in new_name.lower() and src_table != out_table:
            new_name = re.sub(re.escape(src_table), out_table, new_name, flags=re.IGNORECASE)
        base, n = new_name, 2
        while con.execute("SELECT 1 FROM main.sqlite_master WHERE lower(name)=lower(?)",
                          (new_name,)).fetchone():
            new_name = "{0}_{1}".format(base, n)
            n += 1
        sql = re.sub(r'^(\s*CREATE\s+(?:UNIQUE\s+)?(?:INDEX|TRIGGER)\s+(?:IF\s+NOT\s+EXISTS\s+)?)'
                     r'(?:"(?:[^"]|"")*"|\[[^\]]*\]|`[^`]*`|[^\s]+)',
                     lambda m: m.group(1) + q(new_name), sql, count=1, flags=re.IGNORECASE)
        try:
            con.execute(sql)
        except Exception as e:  # optional objects – never fail the merge for them
            failed.append("{0}: {1}".format(row["name"], e))
    return failed


# ---------------------------------------------------------------------------
# spatial reference systems
# ---------------------------------------------------------------------------
class SrsMapper(object):
    """Maps srs_id of the current source to an srs_id in the output,
    inserting definitions that are missing."""

    def __init__(self, con):
        self.con = con
        self.cache = {}

    def reset(self):
        self.cache = {}

    def map(self, srs_id):
        if srs_id is None:
            return None
        if srs_id in self.cache:
            return self.cache[srs_id]
        con = self.con
        src = _rows(con, "SELECT * FROM src.gpkg_spatial_ref_sys WHERE srs_id = ?", (srs_id,))
        if not src:
            self.cache[srs_id] = srs_id
            return srs_id
        src = src[0]
        org = (src.get("organization") or "").upper()
        org_id = src.get("organization_coordsys_id")
        same = _rows(con, "SELECT * FROM main.gpkg_spatial_ref_sys WHERE srs_id = ?", (srs_id,))
        if same and (self._same(same[0], src)):
            new_id = srs_id
        else:
            new_id = None
            if org and org != "NONE":
                hit = con.execute(
                    "SELECT srs_id FROM main.gpkg_spatial_ref_sys "
                    "WHERE upper(organization) = ? AND organization_coordsys_id = ?",
                    (org, org_id)).fetchone()
                if hit:
                    new_id = hit[0]
            if new_id is None:
                if same:
                    new_id = con.execute(
                        "SELECT max(srs_id) + 1 FROM main.gpkg_spatial_ref_sys").fetchone()[0]
                    new_id = max(new_id, 100000)
                else:
                    new_id = srs_id
                row = dict(src)
                row["srs_id"] = new_id
                _insert_row(con, "gpkg_spatial_ref_sys", row)
        self.cache[srs_id] = new_id
        return new_id

    @staticmethod
    def _same(a, b):
        if (a.get("organization") or "").upper() == (b.get("organization") or "").upper() and \
                a.get("organization_coordsys_id") == b.get("organization_coordsys_id") and \
                (a.get("organization") or "").upper() not in ("", "NONE"):
            return True
        da = re.sub(r"\s+", "", a.get("definition") or "")
        db = re.sub(r"\s+", "", b.get("definition") or "")
        return da == db


# ---------------------------------------------------------------------------
# extensions
# ---------------------------------------------------------------------------
def ensure_extensions_table(con):
    if not has_table(con, "main", "gpkg_extensions"):
        con.execute("CREATE TABLE gpkg_extensions (table_name TEXT, column_name TEXT, "
                    "extension_name TEXT NOT NULL, definition TEXT NOT NULL, "
                    "scope TEXT NOT NULL, CONSTRAINT ge_tce UNIQUE "
                    "(table_name, column_name, extension_name))")


def copy_extensions(con, src_table, out_table):
    """Extension rows registered for one table."""
    if not has_table(con, "src", "gpkg_extensions"):
        return
    ensure_extensions_table(con)
    for row in _rows(con, "SELECT * FROM src.gpkg_extensions WHERE lower(table_name) = lower(?)",
                     (src_table,)):
        row["table_name"] = out_table
        _add_extension(con, row)


def copy_system_extensions(con):
    """Extension rows for GeoPackage system tables (e.g. gridded coverage
    ancillary tables, metadata, crs_wkt) that exist in the output."""
    if not has_table(con, "src", "gpkg_extensions"):
        return
    ensure_extensions_table(con)
    for row in _rows(con, "SELECT * FROM src.gpkg_extensions WHERE table_name IS NOT NULL"):
        t = row["table_name"]
        if not t.lower().startswith(("gpkg_", "gpkgext_")) or not has_table(con, "main", t):
            continue
        col = row.get("column_name")
        if col and col.lower() not in {c.lower() for c in columns(con, "main", t)}:
            continue
        _add_extension(con, row)


def _add_extension(con, row):
    exists = con.execute(
        "SELECT 1 FROM main.gpkg_extensions WHERE lower(coalesce(table_name,'')) = lower(?) "
        "AND lower(coalesce(column_name,'')) = lower(?) AND extension_name = ?",
        (row.get("table_name") or "", row.get("column_name") or "",
         row["extension_name"])).fetchone()
    if not exists:
        _insert_row(con, "gpkg_extensions", row)


# ---------------------------------------------------------------------------
# tile pyramids / gridded coverages / vector tiles
# ---------------------------------------------------------------------------
def copy_tile_object(con, src_name, out_name, srs, mapping):
    con.execute(_rename_header(_master_sql(con, src_name), out_name))
    copy_rows(con, src_name, out_name)
    failed = _copy_dependents(con, src_name, out_name, mapping)

    content = _rows(con, "SELECT * FROM src.gpkg_contents WHERE lower(table_name) = lower(?)",
                    (src_name,))[0]
    content["table_name"] = out_name
    content["srs_id"] = srs.map(content.get("srs_id"))
    ident = content.get("identifier") or out_name
    if ident == src_name:
        ident = out_name
    base, n = ident, 2
    while con.execute("SELECT 1 FROM main.gpkg_contents WHERE identifier = ?", (ident,)).fetchone():
        ident = "{0} ({1})".format(base, n)
        n += 1
    content["identifier"] = ident
    _insert_row(con, "gpkg_contents", content)

    for system in ("gpkg_tile_matrix_set", "gpkg_tile_matrix"):
        ensure_table_like(con, system)
        for row in _rows(con, "SELECT * FROM src.{0} WHERE lower(table_name) = lower(?)".format(  # nosec B608
                q(system)), (src_name,)):
            row["table_name"] = out_name
            if "srs_id" in row:
                row["srs_id"] = srs.map(row["srs_id"])
            _insert_row(con, system, row)

    # 2D gridded coverage ancillary data (+ the EPSG:4979 row it requires)
    if content.get("data_type") == "2d-gridded-coverage":
        srs.map(4979)
    if has_table(con, "src", "gpkg_2d_gridded_coverage_ancillary"):
        ensure_table_like(con, "gpkg_2d_gridded_coverage_ancillary")
        for row in _rows(con, "SELECT * FROM src.gpkg_2d_gridded_coverage_ancillary "
                              "WHERE lower(tile_matrix_set_name) = lower(?)", (src_name,)):
            row.pop("id", None)
            row["tile_matrix_set_name"] = out_name
            _insert_row(con, "gpkg_2d_gridded_coverage_ancillary", row)
    if has_table(con, "src", "gpkg_2d_gridded_tile_ancillary"):
        ensure_table_like(con, "gpkg_2d_gridded_tile_ancillary")
        for row in _rows(con, "SELECT * FROM src.gpkg_2d_gridded_tile_ancillary "
                              "WHERE lower(tpudt_name) = lower(?)", (src_name,)):
            row.pop("id", None)
            row["tpudt_name"] = out_name
            _insert_row(con, "gpkg_2d_gridded_tile_ancillary", row)

    copy_extensions(con, src_name, out_name)
    return failed


# ---------------------------------------------------------------------------
# plain tables and views
# ---------------------------------------------------------------------------
def copy_plain_table(con, src_name, out_name, mapping):
    con.execute(_rename_header(_master_sql(con, src_name), out_name))
    copy_rows(con, src_name, out_name)
    return _copy_dependents(con, src_name, out_name, mapping)


def create_view(con, src_name, out_name, mapping):
    """Re-create a view, rewriting table names.  Returns None on success or
    the SQLite error text (the view is then left out)."""
    sql = _master_sql(con, src_name, types=("view",))
    con.execute("SAVEPOINT view_copy")
    try:
        sql = _rename_header(rename_identifiers(sql, mapping), out_name)
        con.execute(sql)
        con.execute("SELECT * FROM main.{0} LIMIT 0".format(q(out_name)))  # nosec B608
        con.execute("RELEASE view_copy")
        return None
    except Exception as e:
        con.execute("ROLLBACK TO view_copy")
        con.execute("RELEASE view_copy")
        return str(e)


# ---------------------------------------------------------------------------
# metadata
# ---------------------------------------------------------------------------
def _ensure_metadata_tables(con):
    for t in ("gpkg_metadata", "gpkg_metadata_reference"):
        if not has_table(con, "main", t):
            ensure_table_like(con, t)


def copy_metadata(con, src_table, out_table, skip_gdal, id_map):
    """Copy metadata attached to one table (scope table/column/row)."""
    if not (has_table(con, "src", "gpkg_metadata_reference") and
            has_table(con, "src", "gpkg_metadata")):
        return 0
    refs = _rows(con, "SELECT * FROM src.gpkg_metadata_reference "
                      "WHERE lower(table_name) = lower(?)", (src_table,))
    n = 0
    for ref in refs:
        md = _rows(con, "SELECT * FROM src.gpkg_metadata WHERE id = ?", (ref["md_file_id"],))
        if not md:
            continue
        if skip_gdal and md[0].get("md_standard_uri") == GDAL_MD_URI:
            continue
        _ensure_metadata_tables(con)
        ref["md_file_id"] = _copy_md_row(con, md[0], id_map)
        if ref.get("md_parent_id") is not None:
            ref["md_parent_id"] = id_map.get(ref["md_parent_id"])
        ref["table_name"] = out_table
        _insert_row(con, "gpkg_metadata_reference", ref)
        n += 1
    return n


def copy_geopackage_metadata(con, id_map):
    """Metadata that describes the whole GeoPackage (skipped if identical
    metadata is already present)."""
    if not (has_table(con, "src", "gpkg_metadata_reference") and
            has_table(con, "src", "gpkg_metadata")):
        return
    for ref in _rows(con, "SELECT * FROM src.gpkg_metadata_reference "
                          "WHERE reference_scope = 'geopackage'"):
        md = _rows(con, "SELECT * FROM src.gpkg_metadata WHERE id = ?", (ref["md_file_id"],))
        if not md:
            continue
        _ensure_metadata_tables(con)
        dup = con.execute(
            "SELECT 1 FROM main.gpkg_metadata m JOIN main.gpkg_metadata_reference r "
            "ON r.md_file_id = m.id WHERE r.reference_scope = 'geopackage' "
            "AND m.metadata = ? AND m.md_standard_uri = ?",
            (md[0].get("metadata"), md[0].get("md_standard_uri"))).fetchone()
        if dup:
            continue
        ref["md_file_id"] = _copy_md_row(con, md[0], id_map)
        ref["md_parent_id"] = None
        ref["table_name"] = None
        _insert_row(con, "gpkg_metadata_reference", ref)


def _copy_md_row(con, md, id_map):
    old = md["id"]
    if old in id_map:
        return id_map[old]
    row = dict(md)
    row.pop("id", None)
    _insert_row(con, "gpkg_metadata", row)
    new = con.execute("SELECT last_insert_rowid()").fetchone()[0]
    id_map[old] = new
    return new


# ---------------------------------------------------------------------------
# related tables extension
# ---------------------------------------------------------------------------
def copy_relations(con, mapping, kept):
    """Copy gpkgext_relations rows whose tables were all copied from this
    source.  *mapping* old->new names, *kept* = lower-case names copied from
    this source."""
    if not has_table(con, "src", "gpkgext_relations"):
        return 0
    ensure_table_like(con, "gpkgext_relations")
    n = 0
    for row in _rows(con, "SELECT * FROM src.gpkgext_relations"):
        names = [row.get("base_table_name"), row.get("related_table_name"),
                 row.get("mapping_table_name")]
        if not all(x and x.lower() in kept for x in names):
            continue
        new = dict(row)
        new.pop("id", None)
        for k in ("base_table_name", "related_table_name", "mapping_table_name"):
            new[k] = mapping.get(row[k].lower(), row[k])
        if con.execute("SELECT 1 FROM main.gpkgext_relations WHERE lower(base_table_name)=lower(?) "
                       "AND lower(related_table_name)=lower(?) AND lower(mapping_table_name)=lower(?)",
                       (new["base_table_name"], new["related_table_name"],
                        new["mapping_table_name"])).fetchone():
            continue
        _insert_row(con, "gpkgext_relations", new)
        copy_extensions(con, row["mapping_table_name"], new["mapping_table_name"])
        n += 1
    copy_extensions(con, "gpkgext_relations", "gpkgext_relations")
    return n
