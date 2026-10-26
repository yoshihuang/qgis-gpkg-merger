# -*- coding: utf-8 -*-
"""Translation helpers.

All user-visible strings go through :func:`tr`, which uses a single Qt
translation context (``GpkgMerger``).  When Qt is not available (e.g. when
the merge engine is run from plain Python for testing) the English source
text is returned unchanged.
"""

CONTEXT = "GpkgMerger"

try:  # pragma: no cover - depends on runtime
    from qgis.PyQt.QtCore import QCoreApplication

    def tr(text):
        return QCoreApplication.translate(CONTEXT, text)

except Exception:  # pragma: no cover - plain Python / tests

    def tr(text):
        return text


# QGIS uses names such as "zh-Hant" / "zh-Hans" for Chinese, while other
# software uses "zh_TW" / "zh_CN".  Map all of them to the files we ship.
_ALIASES = {
    "zh_hant": "zh_TW",
    "zh_tw": "zh_TW",
    "zh_hk": "zh_TW",
    "zh_mo": "zh_TW",
    "zh_hans": "zh_CN",
    "zh_cn": "zh_CN",
    "zh_sg": "zh_CN",
    "zh": "zh_CN",
}

SUPPORTED = ["en", "zh_TW", "zh_CN", "ja", "ko", "de", "fr", "es"]


def normalize_locale(locale_name):
    """Return the translation file suffix to use for a QGIS locale string.

    >>> normalize_locale("zh-Hant")
    'zh_TW'
    >>> normalize_locale("de_AT")
    'de'
    """
    if not locale_name:
        return "en"
    key = str(locale_name).strip().replace("-", "_").lower()
    if key in _ALIASES:
        return _ALIASES[key]
    # e.g. "zh_Hant_TW"
    for alias, target in _ALIASES.items():
        if key.startswith(alias + "_"):
            return target
    short = key.split("_")[0]
    return short if short in SUPPORTED else "en"
