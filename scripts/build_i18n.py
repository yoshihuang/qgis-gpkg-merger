# -*- coding: utf-8 -*-
"""Build the plugin translations.

    python scripts/build_i18n.py

1. collects every tr("...") string in gpkg_merger/*.py
2. checks that scripts/translations.py has a translation for each one
3. writes gpkg_merger/i18n/gpkg_merger_<lang>.ts
4. compiles them to .qm with lrelease (Qt Linguist tools)

To add a language: add its code to LANGS and a column to every entry of T.
"""
import ast
import glob
import os
import shutil
import subprocess
import sys
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLUGIN = os.path.join(ROOT, "gpkg_merger")
I18N = os.path.join(PLUGIN, "i18n")
CONTEXT = "GpkgMerger"

sys.path.insert(0, HERE)
from translations import LANGS, T  # noqa: E402


def collect():
    found = []
    for path in sorted(glob.glob(os.path.join(PLUGIN, "*.py"))):
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "tr"
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                rel = os.path.relpath(path, PLUGIN)
                found.append((node.args[0].value, rel, node.lineno))
    return found


def main():
    found = collect()
    sources = []
    for text, _f, _l in found:
        if text not in sources:
            sources.append(text)
    missing = [s for s in sources if s not in T]
    unused = [s for s in T if s not in sources]
    bad = [s for s, v in T.items() if len(v) != len(LANGS)]
    if missing or bad:
        for s in missing:
            print("MISSING translation:", repr(s))
        for s in bad:
            print("WRONG column count:", repr(s))
        sys.exit(1)
    for s in unused:
        print("note: unused translation", repr(s))

    os.makedirs(I18N, exist_ok=True)
    lrelease = shutil.which("lrelease") or shutil.which("lrelease-qt5") or shutil.which("lrelease-qt6")
    for li, lang in enumerate(LANGS):
        ts = os.path.join(I18N, "gpkg_merger_{0}.ts".format(lang))
        lines = ['<?xml version="1.0" encoding="utf-8"?>',
                 '<!DOCTYPE TS>',
                 '<TS version="2.1" language="{0}" sourcelanguage="en">'.format(lang),
                 '<context>', '    <name>{0}</name>'.format(CONTEXT)]
        for text in sources:
            locs = [(f, l) for t, f, l in found if t == text]
            lines.append('    <message>')
            for f, l in locs:
                lines.append('        <location filename="../{0}" line="{1}"/>'.format(f, l))
            lines.append('        <source>{0}</source>'.format(escape(text)))
            lines.append('        <translation>{0}</translation>'.format(escape(T[text][li])))
            lines.append('    </message>')
        lines += ['</context>', '</TS>', '']
        with open(ts, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines))
        if lrelease:
            qm = ts[:-3] + ".qm"
            subprocess.check_call([lrelease, "-silent", ts, "-qm", qm])
            print("built", os.path.relpath(qm, ROOT))
        else:
            print("wrote", os.path.relpath(ts, ROOT), "(lrelease not found – .qm not built)")


if __name__ == "__main__":
    main()
