# -*- coding: utf-8 -*-
"""Print the GitHub release notes for one version, taken from CHANGELOG.md.

    python scripts/release_notes.py            # version from metadata.txt
    python scripts/release_notes.py 1.2.0      # a given version

Exits with an error when CHANGELOG.md has no "## <version>" section, so a
release cannot be published without its changelog entry.
"""
import configparser
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/yoshihuang/qgis-gpkg-merger"


def current_version():
    meta = configparser.ConfigParser()
    meta.read(os.path.join(ROOT, "gpkg_merger", "metadata.txt"), encoding="utf-8")
    return meta["general"]["version"]


def section(version):
    with open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"^##\s+v?" + re.escape(version) + r"\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        return None
    return m.group(1).strip()


def notes(version):
    body = section(version)
    if not body:
        raise SystemExit("CHANGELOG.md has no section '## {0}'".format(version))
    return "\n".join([
        "## What's changed",
        "",
        body,
        "",
        "## Install",
        "",
        "Download `gpkg_merger-{0}.zip` below, then in QGIS: "
        "**Plugins ▸ Manage and Install Plugins ▸ Install from ZIP**. "
        "Works with QGIS 3.22 – 3.x and QGIS 4.x.".format(version),
        "",
        "安裝：下載下方的 `gpkg_merger-{0}.zip`，在 QGIS「外掛 ▸ 管理與安裝外掛 ▸ "
        "從 ZIP 安裝」選取。".format(version),
        "",
        "Full history: [CHANGELOG.md]({0}/blob/main/CHANGELOG.md)".format(REPO),
        "",
    ])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(notes(sys.argv[1] if len(sys.argv) > 1 else current_version()))
