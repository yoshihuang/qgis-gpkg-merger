<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="zh_TW" sourcelanguage="en">
<context>
    <name>GpkgMerger</name>
    <message>
        <location filename="../dialog.py" line="76"/>
        <source>GPKG Merger – merge GeoPackages</source>
        <translation>GPKG Merger – 合併 GeoPackage</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="89"/>
        <source>1. Input GeoPackages (merge order: top → bottom)</source>
        <translation>1. 輸入 GeoPackage（併入順序：由上而下）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="92"/>
        <source>Drag items to change the merge order. You can also drop .gpkg files here.</source>
        <translation>拖曳項目可調整併入順序，也可將 .gpkg 檔直接拖放到這裡。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="96"/>
        <source>Add…</source>
        <translation>加入…</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="97"/>
        <source>Remove</source>
        <translation>移除</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="98"/>
        <source>Move up</source>
        <translation>上移</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="99"/>
        <source>Move down</source>
        <translation>下移</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="100"/>
        <source>Clear</source>
        <translation>清除</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="108"/>
        <source>2. Contents and result preview</source>
        <translation>2. 內容與結果預覽</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="126"/>
        <source>3. Layers with the same name</source>
        <translation>3. 同名圖層處理方式</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="128"/>
        <source>Keep all – rename to &lt;gpkg name&gt;_&lt;layer name&gt;</source>
        <translation>不複寫 – 全部保留並改名為 &lt;gpkg名稱&gt;_&lt;圖層名稱&gt;</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="129"/>
        <source>Overwrite – a later file replaces earlier ones</source>
        <translation>複寫 – 依併入順序，後面的檔案覆蓋前面的</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="130"/>
        <source>Append – merge features into one layer (geometry type, CRS and fields must match)</source>
        <translation>擴充 – 將圖徵併入同一圖層（幾何類型、座標系統與欄位須一致）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="139"/>
        <source>4. Output</source>
        <translation>4. 輸出</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="143"/>
        <location filename="../dialog.py" line="227"/>
        <source>GeoPackage (*.gpkg)</source>
        <translation>GeoPackage (*.gpkg)</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="144"/>
        <source>Output GeoPackage</source>
        <translation>輸出 GeoPackage</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="147"/>
        <source>Copy QGIS layer styles (layer_styles table)</source>
        <translation>一併複製 QGIS 圖層樣式（layer_styles 表）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="149"/>
        <source>Add merged layers to the project</source>
        <translation>將合併後的圖層加入專案</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="173"/>
        <source>Merge</source>
        <translation>合併</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="175"/>
        <source>Cancel</source>
        <translation>取消</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="177"/>
        <source>Close</source>
        <translation>關閉</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="227"/>
        <source>Select GeoPackages</source>
        <translation>選擇 GeoPackage</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="479"/>
        <location filename="../dialog.py" line="254"/>
        <location filename="../dialog.py" line="402"/>
        <location filename="../dialog.py" line="407"/>
        <location filename="../dialog.py" line="415"/>
        <location filename="../dialog.py" line="444"/>
        <location filename="../dialog.py" line="424"/>
        <location filename="../dialog.py" line="468"/>
        <source>GPKG Merger</source>
        <translation>GPKG Merger</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="111"/>
        <source>Layer</source>
        <translation>圖層</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="111"/>
        <source>Type</source>
        <translation>類型</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="111"/>
        <source>CRS</source>
        <translation>座標系統</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="112"/>
        <source>Count</source>
        <translation>數量</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="112"/>
        <source>Result</source>
        <translation>結果</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="295"/>
        <location filename="../dialog.py" line="403"/>
        <source>Add at least two GeoPackages to merge.</source>
        <translation>請至少加入兩個 GeoPackage 才能合併。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="370"/>
        <source>Append is not possible – change the order, remove files or choose another option.</source>
        <translation>無法擴充 – 請調整順序、移除檔案或改選其他方式。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="408"/>
        <source>Please choose an output file.</source>
        <translation>請選擇輸出檔案。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="416"/>
        <location filename="../merge_core.py" line="529"/>
        <source>The output file must not be one of the input files.</source>
        <translation>輸出檔不可與輸入檔相同。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="431"/>
        <source>Merge stopped:</source>
        <translation>合併已停止：</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="435"/>
        <source>Layers cannot be appended</source>
        <translation>圖層無法擴充</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="476"/>
        <source>QGIS projects were merged as well. Open them with Project ▸ Open From ▸ GeoPackage.</source>
        <translation>QGIS 專案也已一併合併，可從「專案 ▸ 開啟自 ▸ GeoPackage」開啟。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="367"/>
        <source>{0} files, {1} output objects, {2} QGIS projects, {3} duplicate names.</source>
        <translation>{0} 個檔案，輸出 {1} 個物件、{2} 個 QGIS 專案，{3} 個重複名稱。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="463"/>
        <source>Cancelled. No output was written.</source>
        <translation>已取消，未寫入任何輸出。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="480"/>
        <source>{0} layers written to {1}</source>
        <translation>已寫入 {0} 個圖層至 {1}</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="309"/>
        <location filename="../dialog.py" line="354"/>
        <source>copy</source>
        <translation>複製</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="330"/>
        <source>INCOMPATIBLE – cannot append</source>
        <translation>格式不符 – 無法擴充</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="345"/>
        <source>This layer name exists in more than one file.</source>
        <translation>此圖層名稱出現在多個檔案中。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="350"/>
        <location filename="../dialog.py" line="334"/>
        <source>dropped (overwritten by a later file)</source>
        <translation>捨棄（被後面的檔案覆蓋）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="355"/>
        <source>QGIS project</source>
        <translation>QGIS 專案</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="436"/>
        <source>The following layers have a different structure and cannot be appended. Nothing was written.

Change the merge order, remove files or choose another option, then try again.</source>
        <translation>下列圖層的向量格式不一致，無法擴充，未寫入任何資料。

請調整併入順序、移除檔案或改選其他處理方式後再試一次。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="445"/>
        <source>The file already exists:
{0}

Replace it?</source>
        <translation>檔案已存在：
{0}

要取代嗎？</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="305"/>
        <source>append to '{0}'</source>
        <translation>擴充至「{0}」</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="467"/>
        <location filename="../dialog.py" line="468"/>
        <source>Error: {0}</source>
        <translation>錯誤：{0}</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="513"/>
        <source>Could not load layer '{0}'</source>
        <translation>無法載入圖層「{0}」</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="307"/>
        <location filename="../dialog.py" line="352"/>
        <source>rename to '{0}'</source>
        <translation>改名為「{0}」</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="361"/>
        <source>skipped: {0}</source>
        <translation>略過：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="141"/>
        <source>Raster (tiles)</source>
        <translation>網格（圖磚）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="143"/>
        <source>Table (not registered)</source>
        <translation>資料表（未註冊）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="145"/>
        <source>View</source>
        <translation>檢視表</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="147"/>
        <source>No geometry</source>
        <translation>無幾何</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="522"/>
        <source>The merge plan contains errors; nothing was written.</source>
        <translation>合併計畫有錯誤，未寫入任何資料。</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="524"/>
        <source>There is nothing to merge.</source>
        <translation>沒有可合併的圖層。</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="138"/>
        <source>Raster (gridded coverage)</source>
        <translation>網格（數值網格，如 DEM）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="140"/>
        <source>Vector tiles</source>
        <translation>向量圖磚</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="621"/>
        <source>Done: {0}</source>
        <translation>完成：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="360"/>
        <source>geometry type differs ({0} vs {1})</source>
        <translation>幾何類型不同（{0} 與 {1}）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="365"/>
        <location filename="../merge_core.py" line="368"/>
        <source>coordinate reference system differs ({0} vs {1})</source>
        <translation>座標系統不同（{0} 與 {1}）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="366"/>
        <location filename="../merge_core.py" line="366"/>
        <source>none</source>
        <translation>無</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="376"/>
        <source>missing fields: {0}</source>
        <translation>缺少欄位：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="378"/>
        <source>extra fields: {0}</source>
        <translation>多出欄位：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="716"/>
        <source>Copying QGIS project '{0}' from '{1}' as '{2}'</source>
        <translation>複製「{1}」的 QGIS 專案「{0}」為「{2}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="236"/>
        <location filename="../merge_core.py" line="281"/>
        <location filename="../merge_core.py" line="327"/>
        <location filename="../merge_core.py" line="234"/>
        <source>Cannot open GeoPackage: {0}</source>
        <translation>無法開啟 GeoPackage：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="381"/>
        <source>field '{0}' type differs ({1} vs {2})</source>
        <translation>欄位「{0}」型別不同（{1} 與 {2}）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="461"/>
        <source>only vector and attribute layers can be appended</source>
        <translation>只有向量與屬性圖層可以擴充</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="506"/>
        <source>Skipped '{0}' in '{1}': {2}</source>
        <translation>略過「{1}」中的「{0}」：{2}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="438"/>
        <source>Layer '{0}' of '{1}' renamed to '{2}'</source>
        <translation>「{1}」的圖層「{0}」改名為「{2}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="598"/>
        <source>Copying layer styles from '{0}'</source>
        <translation>複製「{0}」的圖層樣式</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="686"/>
        <source>View '{0}' of '{1}' could not be re-created and was skipped: {2}</source>
        <translation>「{1}」的檢視表「{0}」無法重建，已略過：{2}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="689"/>
        <source>Copying view '{0}' from '{1}' as '{2}'</source>
        <translation>複製「{1}」的檢視表「{0}」為「{2}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="456"/>
        <source>Layer '{0}' of '{1}' is overwritten by '{2}'</source>
        <translation>「{1}」的圖層「{0}」被「{2}」覆蓋</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="495"/>
        <source>Project '{0}' of '{1}' is overwritten by '{2}'</source>
        <translation>「{1}」的專案「{0}」被「{2}」覆蓋</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="501"/>
        <source>Project '{0}' of '{1}' renamed to '{2}'</source>
        <translation>「{1}」的專案「{0}」改名為「{2}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="567"/>
        <source>Copying '{0}' from '{1}' as '{2}'</source>
        <translation>複製「{1}」的「{0}」為「{2}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="578"/>
        <source>Appending '{0}' from '{1}' to '{2}'</source>
        <translation>將「{1}」的「{0}」擴充至「{2}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="665"/>
        <source>Copying relations from '{0}'</source>
        <translation>複製「{0}」的關聯</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="645"/>
        <source>Copying raster '{0}' from '{1}' as '{2}'</source>
        <translation>複製「{1}」的網格「{0}」為「{2}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="659"/>
        <source>Index or trigger skipped: {0}</source>
        <translation>略過索引或觸發器：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="470"/>
        <source>Layer '{0}': '{1}' cannot be appended to '{2}': {3}</source>
        <translation>圖層「{0}」：「{1}」無法擴充至「{2}」：{3}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="474"/>
        <source>{0} features of '{1}' in '{2}' appended to layer '{3}'</source>
        <translation>「{2}」中「{1}」的 {0} 筆圖徵擴充至圖層「{3}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="650"/>
        <source>Copying table '{0}' from '{1}' as '{2}'</source>
        <translation>複製「{1}」的資料表「{0}」為「{2}」</translation>
    </message>
    <message>
        <location filename="../plugin.py" line="58"/>
        <source>Merge GeoPackages…</source>
        <translation>合併 GeoPackage…</translation>
    </message>
    <message>
        <location filename="../plugin.py" line="59"/>
        <source>Merge several GeoPackage files into one</source>
        <translation>將多個 GeoPackage 檔合併為一個</translation>
    </message>
    <message>
        <location filename="../plugin.py" line="61"/>
        <location filename="../plugin.py" line="66"/>
        <source>&amp;GPKG Merger</source>
        <translation>&amp;GPKG Merger</translation>
    </message>
</context>
</TS>
