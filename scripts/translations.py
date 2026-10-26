# -*- coding: utf-8 -*-
"""Translation table.  English source text -> translations.

Column order is LANGS.  Run ``python scripts/build_i18n.py`` after editing:
it checks that every tr("…") string of the plugin is listed here, writes
the Qt .ts files and compiles them to .qm with lrelease.
"""

LANGS = ["zh_TW", "zh_CN", "ja", "ko", "de", "fr", "es"]

T = {
    "GPKG Merger – merge GeoPackages": (
        "GPKG Merger – 合併 GeoPackage",
        "GPKG Merger – 合并 GeoPackage",
        "GPKG Merger – GeoPackage の結合",
        "GPKG Merger – GeoPackage 병합",
        "GPKG Merger – GeoPackages zusammenführen",
        "GPKG Merger – fusionner des GeoPackages",
        "GPKG Merger – combinar GeoPackages"),
    "1. Input GeoPackages (merge order: top → bottom)": (
        "1. 輸入 GeoPackage（併入順序：由上而下）",
        "1. 输入 GeoPackage（合并顺序：从上到下）",
        "1. 入力 GeoPackage（結合順序：上 → 下）",
        "1. 입력 GeoPackage (병합 순서: 위 → 아래)",
        "1. Eingabe-GeoPackages (Reihenfolge: oben → unten)",
        "1. GeoPackages en entrée (ordre de fusion : haut → bas)",
        "1. GeoPackages de entrada (orden: arriba → abajo)"),
    "Drag items to change the merge order. You can also drop .gpkg files here.": (
        "拖曳項目可調整併入順序，也可將 .gpkg 檔直接拖放到這裡。",
        "拖动项目可调整合并顺序，也可将 .gpkg 文件直接拖放到这里。",
        "項目をドラッグして結合順序を変更できます。.gpkg ファイルをここにドロップすることもできます。",
        "항목을 끌어 병합 순서를 바꿀 수 있습니다. .gpkg 파일을 여기에 끌어다 놓을 수도 있습니다.",
        "Einträge ziehen, um die Reihenfolge zu ändern. .gpkg-Dateien können auch hier abgelegt werden.",
        "Faites glisser les éléments pour changer l'ordre. Vous pouvez aussi déposer des fichiers .gpkg ici.",
        "Arrastre los elementos para cambiar el orden. También puede soltar archivos .gpkg aquí."),
    "Add…": ("加入…", "添加…", "追加…", "추가…", "Hinzufügen…", "Ajouter…", "Añadir…"),
    "Remove": ("移除", "移除", "削除", "제거", "Entfernen", "Retirer", "Quitar"),
    "Move up": ("上移", "上移", "上へ", "위로", "Nach oben", "Monter", "Subir"),
    "Move down": ("下移", "下移", "下へ", "아래로", "Nach unten", "Descendre", "Bajar"),
    "Clear": ("清除", "清除", "クリア", "모두 지우기", "Leeren", "Vider", "Vaciar"),
    "2. Layers and result preview": (
        "2. 圖層與結果預覽", "2. 图层与结果预览", "2. レイヤと結果のプレビュー",
        "2. 레이어 및 결과 미리보기", "2. Layer und Ergebnisvorschau",
        "2. Couches et aperçu du résultat", "2. Capas y vista previa del resultado"),
    "3. Layers with the same name": (
        "3. 同名圖層處理方式", "3. 同名图层处理方式", "3. 同名レイヤの扱い",
        "3. 같은 이름의 레이어", "3. Layer mit gleichem Namen",
        "3. Couches portant le même nom", "3. Capas con el mismo nombre"),
    "Keep all – rename to <gpkg name>_<layer name>": (
        "不複寫 – 全部保留並改名為 <gpkg名稱>_<圖層名稱>",
        "不覆盖 – 全部保留并改名为 <gpkg名称>_<图层名称>",
        "上書きしない – <gpkg名>_<レイヤ名> に名前を変更してすべて保持",
        "덮어쓰지 않음 – <gpkg 이름>_<레이어 이름>으로 바꿔 모두 유지",
        "Alle behalten – umbenennen in <GPKG-Name>_<Layername>",
        "Tout conserver – renommer en <nom gpkg>_<nom couche>",
        "Conservar todas – renombrar a <nombre gpkg>_<nombre capa>"),
    "Overwrite – a later file replaces earlier ones": (
        "複寫 – 依併入順序，後面的檔案覆蓋前面的",
        "覆盖 – 按合并顺序，后面的文件覆盖前面的",
        "上書き – 結合順序で後のファイルが前のものを置き換える",
        "덮어쓰기 – 병합 순서상 뒤의 파일이 앞의 것을 대체",
        "Überschreiben – eine spätere Datei ersetzt frühere",
        "Écraser – un fichier suivant remplace les précédents",
        "Sobrescribir – un archivo posterior reemplaza a los anteriores"),
    "Append – merge features into one layer (geometry type, CRS and fields must match)": (
        "擴充 – 將圖徵併入同一圖層（幾何類型、座標系統與欄位須一致）",
        "扩充 – 将要素并入同一图层（几何类型、坐标系与字段须一致）",
        "追加 – 地物を1つのレイヤに統合（ジオメトリ型・CRS・フィールドが一致する必要あり）",
        "추가 – 피처를 하나의 레이어로 병합 (지오메트리 유형, 좌표계, 필드가 일치해야 함)",
        "Anhängen – Objekte in einem Layer vereinen (Geometrietyp, KBS und Felder müssen übereinstimmen)",
        "Ajouter – réunir les entités dans une couche (type de géométrie, SCR et champs identiques)",
        "Anexar – unir los objetos en una capa (tipo de geometría, SRC y campos deben coincidir)"),
    "4. Output": ("4. 輸出", "4. 输出", "4. 出力", "4. 출력", "4. Ausgabe", "4. Sortie", "4. Salida"),
    "GeoPackage (*.gpkg)": (
        "GeoPackage (*.gpkg)", "GeoPackage (*.gpkg)", "GeoPackage (*.gpkg)",
        "GeoPackage (*.gpkg)", "GeoPackage (*.gpkg)", "GeoPackage (*.gpkg)",
        "GeoPackage (*.gpkg)"),
    "Output GeoPackage": (
        "輸出 GeoPackage", "输出 GeoPackage", "出力 GeoPackage", "출력 GeoPackage",
        "Ausgabe-GeoPackage", "GeoPackage de sortie", "GeoPackage de salida"),
    "Copy QGIS layer styles (layer_styles table)": (
        "一併複製 QGIS 圖層樣式（layer_styles 表）",
        "一并复制 QGIS 图层样式（layer_styles 表）",
        "QGIS レイヤスタイルもコピー（layer_styles テーブル）",
        "QGIS 레이어 스타일 복사 (layer_styles 테이블)",
        "QGIS-Layerstile kopieren (Tabelle layer_styles)",
        "Copier les styles de couche QGIS (table layer_styles)",
        "Copiar estilos de capa de QGIS (tabla layer_styles)"),
    "Add merged layers to the project": (
        "將合併後的圖層加入專案", "将合并后的图层加入项目", "結合したレイヤをプロジェクトに追加",
        "병합된 레이어를 프로젝트에 추가", "Zusammengeführte Layer zum Projekt hinzufügen",
        "Ajouter les couches fusionnées au projet", "Añadir las capas combinadas al proyecto"),
    "Merge": ("合併", "合并", "結合", "병합", "Zusammenführen", "Fusionner", "Combinar"),
    "Cancel": ("取消", "取消", "キャンセル", "취소", "Abbrechen", "Annuler", "Cancelar"),
    "Close": ("關閉", "关闭", "閉じる", "닫기", "Schließen", "Fermer", "Cerrar"),
    "Select GeoPackages": (
        "選擇 GeoPackage", "选择 GeoPackage", "GeoPackage を選択", "GeoPackage 선택",
        "GeoPackages auswählen", "Sélectionner des GeoPackages", "Seleccionar GeoPackages"),
    "GPKG Merger": ("GPKG Merger",) * 7,
    "Layer": ("圖層", "图层", "レイヤ", "레이어", "Layer", "Couche", "Capa"),
    "Geometry": ("幾何", "几何", "ジオメトリ", "지오메트리", "Geometrie", "Géométrie", "Geometría"),
    "CRS": ("座標系統", "坐标系", "CRS", "좌표계", "KBS", "SCR", "SRC"),
    "Features": ("圖徵數", "要素数", "地物数", "피처 수", "Objekte", "Entités", "Objetos"),
    "Result": ("結果", "结果", "結果", "결과", "Ergebnis", "Résultat", "Resultado"),
    "Add at least two GeoPackages to merge.": (
        "請至少加入兩個 GeoPackage 才能合併。",
        "请至少添加两个 GeoPackage 才能合并。",
        "結合するには GeoPackage を2つ以上追加してください。",
        "병합하려면 GeoPackage를 두 개 이상 추가하세요.",
        "Mindestens zwei GeoPackages zum Zusammenführen hinzufügen.",
        "Ajoutez au moins deux GeoPackages à fusionner.",
        "Añada al menos dos GeoPackages para combinar."),
    "Append is not possible – change the order, remove files or choose another option.": (
        "無法擴充 – 請調整順序、移除檔案或改選其他方式。",
        "无法扩充 – 请调整顺序、移除文件或改选其他方式。",
        "追加できません – 順序を変更するか、ファイルを削除するか、別の方法を選んでください。",
        "추가할 수 없습니다 – 순서를 바꾸거나 파일을 제거하거나 다른 옵션을 선택하세요.",
        "Anhängen nicht möglich – Reihenfolge ändern, Dateien entfernen oder andere Option wählen.",
        "Ajout impossible – modifiez l'ordre, retirez des fichiers ou choisissez une autre option.",
        "No se puede anexar: cambie el orden, quite archivos o elija otra opción."),
    "Please choose an output file.": (
        "請選擇輸出檔案。", "请选择输出文件。", "出力ファイルを選択してください。",
        "출력 파일을 선택하세요.", "Bitte eine Ausgabedatei wählen.",
        "Veuillez choisir un fichier de sortie.", "Elija un archivo de salida."),
    "The output file must not be one of the input files.": (
        "輸出檔不可與輸入檔相同。", "输出文件不能与输入文件相同。",
        "出力ファイルは入力ファイルと同じにできません。",
        "출력 파일은 입력 파일 중 하나일 수 없습니다.",
        "Die Ausgabedatei darf keine der Eingabedateien sein.",
        "Le fichier de sortie ne doit pas être un des fichiers d'entrée.",
        "El archivo de salida no puede ser uno de los de entrada."),
    "Merge stopped:": (
        "合併已停止：", "合并已停止：", "結合を中止しました：", "병합이 중지되었습니다:",
        "Zusammenführen abgebrochen:", "Fusion arrêtée :", "Combinación detenida:"),
    "Layers cannot be appended": (
        "圖層無法擴充", "图层无法扩充", "レイヤを追加できません", "레이어를 추가할 수 없습니다",
        "Layer können nicht angehängt werden", "Impossible d'ajouter les couches",
        "No se pueden anexar las capas"),
    "{0} files, {1} output layers, {2} duplicate layer names.": (
        "{0} 個檔案，輸出 {1} 個圖層，{2} 個重複圖層名稱。",
        "{0} 个文件，输出 {1} 个图层，{2} 个重复图层名称。",
        "{0} ファイル、出力レイヤ {1}、重複レイヤ名 {2}。",
        "파일 {0}개, 출력 레이어 {1}개, 중복 레이어 이름 {2}개.",
        "{0} Dateien, {1} Ausgabelayer, {2} doppelte Layernamen.",
        "{0} fichiers, {1} couches en sortie, {2} noms de couche en double.",
        "{0} archivos, {1} capas de salida, {2} nombres de capa repetidos."),
    "Cancelled. No output was written.": (
        "已取消，未寫入任何輸出。", "已取消，未写入任何输出。", "キャンセルしました。出力は書き込まれていません。",
        "취소되었습니다. 출력이 저장되지 않았습니다.", "Abgebrochen. Es wurde nichts geschrieben.",
        "Annulé. Aucune sortie n'a été écrite.", "Cancelado. No se escribió ninguna salida."),
    "{0} layers written to {1}": (
        "已寫入 {0} 個圖層至 {1}", "已写入 {0} 个图层至 {1}", "{0} レイヤを {1} に書き込みました",
        "레이어 {0}개를 {1}에 저장했습니다", "{0} Layer nach {1} geschrieben",
        "{0} couches écrites dans {1}", "{0} capas escritas en {1}"),
    "copy": ("複製", "复制", "コピー", "복사", "kopieren", "copier", "copiar"),
    "INCOMPATIBLE – cannot append": (
        "格式不符 – 無法擴充", "格式不符 – 无法扩充", "非互換 – 追加不可", "호환되지 않음 – 추가 불가",
        "INKOMPATIBEL – Anhängen nicht möglich", "INCOMPATIBLE – ajout impossible",
        "INCOMPATIBLE – no se puede anexar"),
    "This layer name exists in more than one file.": (
        "此圖層名稱出現在多個檔案中。", "此图层名称出现在多个文件中。",
        "このレイヤ名は複数のファイルに存在します。", "이 레이어 이름은 여러 파일에 있습니다.",
        "Dieser Layername kommt in mehreren Dateien vor.",
        "Ce nom de couche existe dans plusieurs fichiers.",
        "Este nombre de capa existe en más de un archivo."),
    "The following layers have a different structure and cannot be appended. Nothing was written.\n\nChange the merge order, remove files or choose another option, then try again.": (
        "下列圖層的向量格式不一致，無法擴充，未寫入任何資料。\n\n請調整併入順序、移除檔案或改選其他處理方式後再試一次。",
        "下列图层的矢量格式不一致，无法扩充，未写入任何数据。\n\n请调整合并顺序、移除文件或改选其他处理方式后再试一次。",
        "次のレイヤは構造が異なるため追加できません。何も書き込まれていません。\n\n結合順序を変更するか、ファイルを削除するか、別の方法を選んでから再実行してください。",
        "다음 레이어는 구조가 달라 추가할 수 없습니다. 아무것도 저장되지 않았습니다.\n\n병합 순서를 바꾸거나 파일을 제거하거나 다른 옵션을 선택한 후 다시 시도하세요.",
        "Die folgenden Layer haben eine andere Struktur und können nicht angehängt werden. Es wurde nichts geschrieben.\n\nReihenfolge ändern, Dateien entfernen oder andere Option wählen und erneut versuchen.",
        "Les couches suivantes ont une structure différente et ne peuvent pas être ajoutées. Rien n'a été écrit.\n\nModifiez l'ordre, retirez des fichiers ou choisissez une autre option, puis réessayez.",
        "Las siguientes capas tienen una estructura distinta y no se pueden anexar. No se escribió nada.\n\nCambie el orden, quite archivos o elija otra opción e inténtelo de nuevo."),
    "The file already exists:\n{0}\n\nReplace it?": (
        "檔案已存在：\n{0}\n\n要取代嗎？", "文件已存在：\n{0}\n\n要替换吗？",
        "ファイルは既に存在します：\n{0}\n\n置き換えますか？", "파일이 이미 있습니다:\n{0}\n\n바꾸시겠습니까?",
        "Die Datei existiert bereits:\n{0}\n\nErsetzen?", "Le fichier existe déjà :\n{0}\n\nLe remplacer ?",
        "El archivo ya existe:\n{0}\n\n¿Reemplazarlo?"),
    "append to '{0}'": (
        "擴充至「{0}」", "扩充至“{0}”", "「{0}」に追加", "'{0}'에 추가",
        "an „{0}“ anhängen", "ajouter à « {0} »", "anexar a «{0}»"),
    "dropped (overwritten by a later file)": (
        "捨棄（被後面的檔案覆蓋）", "舍弃（被后面的文件覆盖）", "破棄（後のファイルで上書き）",
        "제외됨 (뒤의 파일로 덮어씀)", "verworfen (von späterer Datei überschrieben)",
        "ignorée (écrasée par un fichier suivant)", "descartada (sobrescrita por un archivo posterior)"),
    "Error: {0}": ("錯誤：{0}", "错误：{0}", "エラー：{0}", "오류: {0}", "Fehler: {0}",
                   "Erreur : {0}", "Error: {0}"),
    "Could not load layer '{0}'": (
        "無法載入圖層「{0}」", "无法加载图层“{0}”", "レイヤ「{0}」を読み込めませんでした",
        "레이어 '{0}'을(를) 불러올 수 없습니다", "Layer „{0}“ konnte nicht geladen werden",
        "Impossible de charger la couche « {0} »", "No se pudo cargar la capa «{0}»"),
    "rename to '{0}'": (
        "改名為「{0}」", "改名为“{0}”", "「{0}」に名前変更", "'{0}'(으)로 이름 변경",
        "umbenennen in „{0}“", "renommer en « {0} »", "renombrar a «{0}»"),
    "skipped: {0}": ("略過：{0}", "跳过：{0}", "スキップ：{0}", "건너뜀: {0}",
                     "übersprungen: {0}", "ignoré : {0}", "omitido: {0}"),
    "No geometry": ("無幾何", "无几何", "ジオメトリなし", "지오메트리 없음", "Keine Geometrie",
                    "Pas de géométrie", "Sin geometría"),
    "The merge plan contains errors; nothing was written.": (
        "合併計畫有錯誤，未寫入任何資料。", "合并计划有错误，未写入任何数据。",
        "結合計画にエラーがあるため、何も書き込まれていません。",
        "병합 계획에 오류가 있어 아무것도 저장되지 않았습니다.",
        "Der Zusammenführungsplan enthält Fehler; es wurde nichts geschrieben.",
        "Le plan de fusion contient des erreurs ; rien n'a été écrit.",
        "El plan de combinación contiene errores; no se escribió nada."),
    "There is nothing to merge.": (
        "沒有可合併的圖層。", "没有可合并的图层。", "結合するものがありません。",
        "병합할 항목이 없습니다.", "Es gibt nichts zusammenzuführen.",
        "Il n'y a rien à fusionner.", "No hay nada que combinar."),
    "Done: {0}": ("完成：{0}", "完成：{0}", "完了：{0}", "완료: {0}", "Fertig: {0}",
                  "Terminé : {0}", "Terminado: {0}"),
    "geometry type differs ({0} vs {1})": (
        "幾何類型不同（{0} 與 {1}）", "几何类型不同（{0} 与 {1}）",
        "ジオメトリ型が異なる（{0} と {1}）", "지오메트리 유형이 다름 ({0} / {1})",
        "Geometrietyp unterschiedlich ({0} / {1})", "type de géométrie différent ({0} / {1})",
        "tipo de geometría distinto ({0} / {1})"),
    "coordinate reference system differs ({0} vs {1})": (
        "座標系統不同（{0} 與 {1}）", "坐标系不同（{0} 与 {1}）",
        "座標参照系が異なる（{0} と {1}）", "좌표계가 다름 ({0} / {1})",
        "Koordinatenbezugssystem unterschiedlich ({0} / {1})",
        "système de coordonnées différent ({0} / {1})",
        "sistema de referencia distinto ({0} / {1})"),
    "none": ("無", "无", "なし", "없음", "keines", "aucun", "ninguno"),
    "missing fields: {0}": ("缺少欄位：{0}", "缺少字段：{0}", "不足フィールド：{0}",
                            "누락된 필드: {0}", "fehlende Felder: {0}",
                            "champs manquants : {0}", "campos que faltan: {0}"),
    "extra fields: {0}": ("多出欄位：{0}", "多出字段：{0}", "余分なフィールド：{0}",
                          "추가 필드: {0}", "zusätzliche Felder: {0}",
                          "champs en trop : {0}", "campos de más: {0}"),
    "Cannot open GeoPackage: {0}": (
        "無法開啟 GeoPackage：{0}", "无法打开 GeoPackage：{0}", "GeoPackage を開けません：{0}",
        "GeoPackage를 열 수 없습니다: {0}", "GeoPackage kann nicht geöffnet werden: {0}",
        "Impossible d'ouvrir le GeoPackage : {0}", "No se puede abrir el GeoPackage: {0}"),
    "QGIS project storage table is not merged": (
        "QGIS 專案儲存表不合併", "QGIS 项目存储表不合并", "QGIS プロジェクト保存テーブルは結合しません",
        "QGIS 프로젝트 저장 테이블은 병합하지 않음", "QGIS-Projekttabelle wird nicht übernommen",
        "la table de projets QGIS n'est pas fusionnée", "la tabla de proyectos de QGIS no se combina"),
    "field '{0}' type differs ({1} vs {2})": (
        "欄位「{0}」型別不同（{1} 與 {2}）", "字段“{0}”类型不同（{1} 与 {2}）",
        "フィールド「{0}」の型が異なる（{1} と {2}）", "필드 '{0}' 유형이 다름 ({1} / {2})",
        "Feldtyp von „{0}“ unterschiedlich ({1} / {2})",
        "type du champ « {0} » différent ({1} / {2})",
        "tipo del campo «{0}» distinto ({1} / {2})"),
    "Skipped '{0}' in '{1}': {2}": (
        "略過「{1}」中的「{0}」：{2}", "跳过“{1}”中的“{0}”：{2}",
        "「{1}」の「{0}」をスキップ：{2}", "'{1}'의 '{0}' 건너뜀: {2}",
        "„{0}“ in „{1}“ übersprungen: {2}", "« {0} » de « {1} » ignoré : {2}",
        "Omitido «{0}» de «{1}»: {2}"),
    "raster/tiles table is not supported": (
        "不支援網格／圖磚資料表", "不支持栅格/瓦片数据表", "ラスタ／タイルテーブルは非対応",
        "래스터/타일 테이블은 지원하지 않음", "Raster-/Kacheltabellen werden nicht unterstützt",
        "les tables raster/tuiles ne sont pas prises en charge",
        "las tablas ráster/teselas no son compatibles"),
    "Layer '{0}' of '{1}' renamed to '{2}'": (
        "「{1}」的圖層「{0}」改名為「{2}」", "“{1}”的图层“{0}”改名为“{2}”",
        "「{1}」のレイヤ「{0}」を「{2}」に名前変更", "'{1}'의 레이어 '{0}' → '{2}'(으)로 이름 변경",
        "Layer „{0}“ aus „{1}“ umbenannt in „{2}“", "Couche « {0} » de « {1} » renommée en « {2} »",
        "Capa «{0}» de «{1}» renombrada a «{2}»"),
    "Layer '{0}' of '{1}' is overwritten by '{2}'": (
        "「{1}」的圖層「{0}」被「{2}」覆蓋", "“{1}”的图层“{0}”被“{2}”覆盖",
        "「{1}」のレイヤ「{0}」は「{2}」で上書きされます", "'{1}'의 레이어 '{0}'은(는) '{2}'(으)로 덮어씀",
        "Layer „{0}“ aus „{1}“ wird durch „{2}“ überschrieben",
        "Couche « {0} » de « {1} » écrasée par « {2} »",
        "Capa «{0}» de «{1}» sobrescrita por «{2}»"),
    "Copying '{0}' from '{1}' as '{2}'": (
        "複製「{1}」的「{0}」為「{2}」", "复制“{1}”的“{0}”为“{2}”",
        "「{1}」の「{0}」を「{2}」としてコピー", "'{1}'의 '{0}'을(를) '{2}'(으)로 복사",
        "Kopiere „{0}“ aus „{1}“ als „{2}“", "Copie de « {0} » de « {1} » en « {2} »",
        "Copiando «{0}» de «{1}» como «{2}»"),
    "Appending '{0}' from '{1}' to '{2}'": (
        "將「{1}」的「{0}」擴充至「{2}」", "将“{1}”的“{0}”扩充至“{2}”",
        "「{1}」の「{0}」を「{2}」に追加", "'{1}'의 '{0}'을(를) '{2}'에 추가",
        "Hänge „{0}“ aus „{1}“ an „{2}“ an", "Ajout de « {0} » de « {1} » à « {2} »",
        "Anexando «{0}» de «{1}» a «{2}»"),
    "Copying layer styles from '{0}'": (
        "複製「{0}」的圖層樣式", "复制“{0}”的图层样式", "「{0}」のレイヤスタイルをコピー",
        "'{0}'의 레이어 스타일 복사", "Kopiere Layerstile aus „{0}“",
        "Copie des styles de couche de « {0} »", "Copiando estilos de capa de «{0}»"),
    "Layer '{0}': '{1}' cannot be appended to '{2}': {3}": (
        "圖層「{0}」：「{1}」無法擴充至「{2}」：{3}", "图层“{0}”：“{1}”无法扩充至“{2}”：{3}",
        "レイヤ「{0}」：「{1}」は「{2}」に追加できません：{3}",
        "레이어 '{0}': '{1}'을(를) '{2}'에 추가할 수 없음: {3}",
        "Layer „{0}“: „{1}“ kann nicht an „{2}“ angehängt werden: {3}",
        "Couche « {0} » : « {1} » ne peut pas être ajouté à « {2} » : {3}",
        "Capa «{0}»: «{1}» no se puede anexar a «{2}»: {3}"),
    "{0} features of '{1}' in '{2}' appended to layer '{3}'": (
        "「{2}」中「{1}」的 {0} 筆圖徵擴充至圖層「{3}」",
        "“{2}”中“{1}”的 {0} 个要素扩充至图层“{3}”",
        "「{2}」の「{1}」の地物 {0} 件をレイヤ「{3}」に追加",
        "'{2}'의 '{1}' 피처 {0}개를 레이어 '{3}'에 추가",
        "{0} Objekte von „{1}“ aus „{2}“ an Layer „{3}“ angehängt",
        "{0} entités de « {1} » (« {2} ») ajoutées à la couche « {3} »",
        "{0} objetos de «{1}» en «{2}» anexados a la capa «{3}»"),
    "Merge GeoPackages…": (
        "合併 GeoPackage…", "合并 GeoPackage…", "GeoPackage を結合…", "GeoPackage 병합…",
        "GeoPackages zusammenführen…", "Fusionner des GeoPackages…", "Combinar GeoPackages…"),
    "Merge several GeoPackage files into one": (
        "將多個 GeoPackage 檔合併為一個", "将多个 GeoPackage 文件合并为一个",
        "複数の GeoPackage ファイルを1つに結合", "여러 GeoPackage 파일을 하나로 병합",
        "Mehrere GeoPackage-Dateien zu einer zusammenführen",
        "Fusionner plusieurs fichiers GeoPackage en un seul",
        "Combinar varios archivos GeoPackage en uno"),
    "&GPKG Merger": ("&GPKG Merger",) * 7,
}
