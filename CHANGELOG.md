# Changelog

## 1.0.1
- Copy layer styles with the OGR feature API instead of SQL (security scan), create full QGIS layer_styles columns
- Remove try/except/pass in locale detection

## 1.0.0
- Ordered merge of several GeoPackages
- Same-name layers: rename (`<gpkg>_<layer>`), overwrite (later wins), append (with geometry/CRS/field check)
- Result preview, layer styles, cancel, temporary output
- UI in English, 繁體中文, 简体中文, 日本語, 한국어, Deutsch, Français, Español following the QGIS locale
