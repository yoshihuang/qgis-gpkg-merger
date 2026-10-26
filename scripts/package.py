# -*- coding: utf-8 -*-
"""Build the zip that is uploaded to https://plugins.qgis.org

    python scripts/package.py          ->  dist/gpkg_merger-<version>.zip
"""
import configparser
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = "gpkg_merger"
SKIP_DIRS = {"__pycache__", ".pytest_cache"}
SKIP_EXT = {".pyc", ".pyo", ".ts"}


def main():
    meta = configparser.ConfigParser()
    meta.read(os.path.join(ROOT, PLUGIN, "metadata.txt"), encoding="utf-8")
    version = meta["general"]["version"]
    if "YOUR_GITHUB_ID" in open(os.path.join(ROOT, PLUGIN, "metadata.txt"), encoding="utf-8").read():
        print("WARNING: metadata.txt still contains YOUR_GITHUB_ID – replace it before uploading.")

    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    out = os.path.join(ROOT, "dist", "{0}-{1}.zip".format(PLUGIN, version))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for folder, dirs, files in os.walk(os.path.join(ROOT, PLUGIN)):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in sorted(files):
                if os.path.splitext(f)[1] in SKIP_EXT:
                    continue
                full = os.path.join(folder, f)
                z.write(full, os.path.relpath(full, ROOT))
        z.write(os.path.join(ROOT, "LICENSE"), PLUGIN + "/LICENSE")
    print(out)


if __name__ == "__main__":
    main()
