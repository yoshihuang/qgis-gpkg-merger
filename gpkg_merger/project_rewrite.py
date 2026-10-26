# -*- coding: utf-8 -*-
"""Rewrite QGIS projects stored inside a GeoPackage (table qgis_projects).

QGIS stores the project as a .qgz (zip) archive, hex encoded, in the
``content`` column.  Layer sources are written relative to the GeoPackage
(``./a.gpkg|layername=roads``, ``GPKG:./a.gpkg:ortho``) or as absolute
paths.  After merging, every reference to *any* of the input GeoPackages
must point to the output file and use the output table name (layers may
have been renamed).
"""

import binascii
import html
import io
import os
import re
import zipfile


def _xml_escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


_ATTR = re.compile(r'="([^"]*)"')
_TEXT = re.compile(r">([^<]+)<")
_WIN_ABS = re.compile(r"^[A-Za-z]:[\\/]")


def _is_abs(path):
    return path.startswith(("/", "\\\\")) or bool(_WIN_ABS.match(path))


def _norm(path):
    return os.path.normcase(os.path.normpath(path))


class SourceRewriter(object):
    """Maps data source strings of any input GeoPackage to the output.

    inputs: list of dicts with keys
        path      absolute path of the input GeoPackage
        tables    {lower-case table name: output table name}
        ogr_order list of OGR layer names (for old ``|layerid=N`` sources)
    """

    def __init__(self, inputs, output_path):
        self.output_path = os.path.abspath(output_path)
        self.inputs = {_norm(os.path.abspath(i["path"])): i for i in inputs}
        self.changed = 0

    def _lookup(self, path, base_dir):
        full = path if _is_abs(path) else os.path.join(base_dir, path)
        return self.inputs.get(_norm(full))

    def _new_path(self, old):
        if _is_abs(old):
            return self.output_path.replace(os.sep, "\\" if "\\" in old else "/")
        return "./" + os.path.basename(self.output_path)

    def rewrite(self, source, base_dir):
        """Return the rewritten source string, or the original."""
        if ".gpkg" not in source.lower():
            return source
        m = re.match(r"^GPKG:(.+):([^:]+)$", source)
        if m:
            info = self._lookup(m.group(1), base_dir)
            if info is None:
                return source
            table = info["tables"].get(m.group(2).lower(), m.group(2))
            self.changed += 1
            return "GPKG:{0}:{1}".format(self._new_path(m.group(1)), table)

        parts = source.split("|")
        info = self._lookup(parts[0], base_dir)
        if info is None:
            return source
        out = [self._new_path(parts[0])]
        for p in parts[1:]:
            key, _, val = p.partition("=")
            if key == "layername":
                p = "layername=" + info["tables"].get(val.lower(), val)
            elif key == "layerid" and val.isdigit():
                order = info.get("ogr_order") or []
                idx = int(val)
                if idx < len(order):
                    name = order[idx]
                    p = "layername=" + info["tables"].get(name.lower(), name)
            out.append(p)
        self.changed += 1
        return "|".join(out)

    def rewrite_xml(self, text, base_dir):
        def _value(raw):
            plain = html.unescape(raw)
            new = self.rewrite(plain, base_dir)
            return raw if new == plain else _xml_escape(new)

        text = _ATTR.sub(lambda m: '="' + _value(m.group(1)) + '"', text)
        text = _TEXT.sub(lambda m: ">" + _value(m.group(1)) + "<", text)
        return text


def decode_content(content):
    """Return (zip bytes, encoder) for a qgis_projects.content value."""
    if isinstance(content, str):
        return binascii.unhexlify(content), lambda b: binascii.hexlify(b).decode("ascii")
    data = bytes(content)
    if data[:2] == b"PK":
        return data, lambda b: b
    return binascii.unhexlify(data), lambda b: binascii.hexlify(b)


def rewrite_project(content, rewriter, base_dir):
    """Rewrite all .qgs files inside a stored project; other archive members
    (auxiliary storage .qgd/.db) are copied unchanged."""
    raw, encode = decode_content(content)
    src = zipfile.ZipFile(io.BytesIO(raw))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename.lower().endswith(".qgs"):
                data = rewriter.rewrite_xml(data.decode("utf-8"), base_dir).encode("utf-8")
            dst.writestr(item, data)
    return encode(buf.getvalue())
