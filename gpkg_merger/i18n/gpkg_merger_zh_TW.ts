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
        <source>2. Layers and result preview</source>
        <translation>2. 圖層與結果預覽</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="125"/>
        <source>3. Layers with the same name</source>
        <translation>3. 同名圖層處理方式</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="127"/>
        <source>Keep all – rename to &lt;gpkg name&gt;_&lt;layer name&gt;</source>
        <translation>不複寫 – 全部保留並改名為 &lt;gpkg名稱&gt;_&lt;圖層名稱&gt;</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="128"/>
        <source>Overwrite – a later file replaces earlier ones</source>
        <translation>複寫 – 依併入順序，後面的檔案覆蓋前面的</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="129"/>
        <source>Append – merge features into one layer (geometry type, CRS and fields must match)</source>
        <translation>擴充 – 將圖徵併入同一圖層（幾何類型、座標系統與欄位須一致）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="138"/>
        <source>4. Output</source>
        <translation>4. 輸出</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="142"/>
        <location filename="../dialog.py" line="224"/>
        <source>GeoPackage (*.gpkg)</source>
        <translation>GeoPackage (*.gpkg)</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="143"/>
        <source>Output GeoPackage</source>
        <translation>輸出 GeoPackage</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="146"/>
        <source>Copy QGIS layer styles (layer_styles table)</source>
        <translation>一併複製 QGIS 圖層樣式（layer_styles 表）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="148"/>
        <source>Add merged layers to the project</source>
        <translation>將合併後的圖層加入專案</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="170"/>
        <source>Merge</source>
        <translation>合併</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="172"/>
        <source>Cancel</source>
        <translation>取消</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="174"/>
        <source>Close</source>
        <translation>關閉</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="224"/>
        <source>Select GeoPackages</source>
        <translation>選擇 GeoPackage</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="457"/>
        <location filename="../dialog.py" line="251"/>
        <location filename="../dialog.py" line="383"/>
        <location filename="../dialog.py" line="388"/>
        <location filename="../dialog.py" line="396"/>
        <location filename="../dialog.py" line="425"/>
        <location filename="../dialog.py" line="405"/>
        <location filename="../dialog.py" line="449"/>
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
        <source>Geometry</source>
        <translation>幾何</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="111"/>
        <source>CRS</source>
        <translation>座標系統</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="112"/>
        <source>Features</source>
        <translation>圖徵數</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="112"/>
        <source>Result</source>
        <translation>結果</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="292"/>
        <location filename="../dialog.py" line="384"/>
        <source>Add at least two GeoPackages to merge.</source>
        <translation>請至少加入兩個 GeoPackage 才能合併。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="351"/>
        <source>Append is not possible – change the order, remove files or choose another option.</source>
        <translation>無法擴充 – 請調整順序、移除檔案或改選其他方式。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="389"/>
        <source>Please choose an output file.</source>
        <translation>請選擇輸出檔案。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="397"/>
        <location filename="../merge_core.py" line="373"/>
        <source>The output file must not be one of the input files.</source>
        <translation>輸出檔不可與輸入檔相同。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="412"/>
        <source>Merge stopped:</source>
        <translation>合併已停止：</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="416"/>
        <source>Layers cannot be appended</source>
        <translation>圖層無法擴充</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="348"/>
        <source>{0} files, {1} output layers, {2} duplicate layer names.</source>
        <translation>{0} 個檔案，輸出 {1} 個圖層，{2} 個重複圖層名稱。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="444"/>
        <source>Cancelled. No output was written.</source>
        <translation>已取消，未寫入任何輸出。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="458"/>
        <source>{0} layers written to {1}</source>
        <translation>已寫入 {0} 個圖層至 {1}</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="306"/>
        <source>copy</source>
        <translation>複製</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="325"/>
        <source>INCOMPATIBLE – cannot append</source>
        <translation>格式不符 – 無法擴充</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="339"/>
        <source>This layer name exists in more than one file.</source>
        <translation>此圖層名稱出現在多個檔案中。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="417"/>
        <source>The following layers have a different structure and cannot be appended. Nothing was written.

Change the merge order, remove files or choose another option, then try again.</source>
        <translation>下列圖層的向量格式不一致，無法擴充，未寫入任何資料。

請調整併入順序、移除檔案或改選其他處理方式後再試一次。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="426"/>
        <source>The file already exists:
{0}

Replace it?</source>
        <translation>檔案已存在：
{0}

要取代嗎？</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="302"/>
        <source>append to '{0}'</source>
        <translation>擴充至「{0}」</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="329"/>
        <source>dropped (overwritten by a later file)</source>
        <translation>捨棄（被後面的檔案覆蓋）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="448"/>
        <location filename="../dialog.py" line="449"/>
        <source>Error: {0}</source>
        <translation>錯誤：{0}</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="482"/>
        <source>Could not load layer '{0}'</source>
        <translation>無法載入圖層「{0}」</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="304"/>
        <source>rename to '{0}'</source>
        <translation>改名為「{0}」</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="342"/>
        <source>skipped: {0}</source>
        <translation>略過：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="105"/>
        <source>No geometry</source>
        <translation>無幾何</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="366"/>
        <source>The merge plan contains errors; nothing was written.</source>
        <translation>合併計畫有錯誤，未寫入任何資料。</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="368"/>
        <source>There is nothing to merge.</source>
        <translation>沒有可合併的圖層。</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="457"/>
        <source>Done: {0}</source>
        <translation>完成：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="244"/>
        <source>geometry type differs ({0} vs {1})</source>
        <translation>幾何類型不同（{0} 與 {1}）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="249"/>
        <location filename="../merge_core.py" line="252"/>
        <source>coordinate reference system differs ({0} vs {1})</source>
        <translation>座標系統不同（{0} 與 {1}）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="250"/>
        <location filename="../merge_core.py" line="250"/>
        <source>none</source>
        <translation>無</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="260"/>
        <source>missing fields: {0}</source>
        <translation>缺少欄位：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="262"/>
        <source>extra fields: {0}</source>
        <translation>多出欄位：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="174"/>
        <location filename="../merge_core.py" line="172"/>
        <source>Cannot open GeoPackage: {0}</source>
        <translation>無法開啟 GeoPackage：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="196"/>
        <source>QGIS project storage table is not merged</source>
        <translation>QGIS 專案儲存表不合併</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="265"/>
        <source>field '{0}' type differs ({1} vs {2})</source>
        <translation>欄位「{0}」型別不同（{1} 與 {2}）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="351"/>
        <source>Skipped '{0}' in '{1}': {2}</source>
        <translation>略過「{1}」中的「{0}」：{2}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="183"/>
        <source>raster/tiles table is not supported</source>
        <translation>不支援網格／圖磚資料表</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="321"/>
        <source>Layer '{0}' of '{1}' renamed to '{2}'</source>
        <translation>「{1}」的圖層「{0}」改名為「{2}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="437"/>
        <source>Copying layer styles from '{0}'</source>
        <translation>複製「{0}」的圖層樣式</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="329"/>
        <source>Layer '{0}' of '{1}' is overwritten by '{2}'</source>
        <translation>「{1}」的圖層「{0}」被「{2}」覆蓋</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="410"/>
        <source>Copying '{0}' from '{1}' as '{2}'</source>
        <translation>複製「{1}」的「{0}」為「{2}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="421"/>
        <source>Appending '{0}' from '{1}' to '{2}'</source>
        <translation>將「{1}」的「{0}」擴充至「{2}」</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="341"/>
        <source>Layer '{0}': '{1}' cannot be appended to '{2}': {3}</source>
        <translation>圖層「{0}」：「{1}」無法擴充至「{2}」：{3}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="346"/>
        <source>{0} features of '{1}' in '{2}' appended to layer '{3}'</source>
        <translation>「{2}」中「{1}」的 {0} 筆圖徵擴充至圖層「{3}」</translation>
    </message>
    <message>
        <location filename="../plugin.py" line="54"/>
        <source>Merge GeoPackages…</source>
        <translation>合併 GeoPackage…</translation>
    </message>
    <message>
        <location filename="../plugin.py" line="55"/>
        <source>Merge several GeoPackage files into one</source>
        <translation>將多個 GeoPackage 檔合併為一個</translation>
    </message>
    <message>
        <location filename="../plugin.py" line="57"/>
        <location filename="../plugin.py" line="62"/>
        <source>&amp;GPKG Merger</source>
        <translation>&amp;GPKG Merger</translation>
    </message>
</context>
</TS>
