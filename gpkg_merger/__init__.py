# -*- coding: utf-8 -*-
"""GPKG Merger – QGIS plugin entry point."""


def classFactory(iface):  # noqa: N802 (QGIS API name)
    from .plugin import GpkgMergerPlugin
    return GpkgMergerPlugin(iface)
