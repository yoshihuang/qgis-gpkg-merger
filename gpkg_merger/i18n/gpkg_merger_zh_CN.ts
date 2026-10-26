<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="zh_CN" sourcelanguage="en">
<context>
    <name>GpkgMerger</name>
    <message>
        <location filename="../dialog.py" line="76"/>
        <source>GPKG Merger – merge GeoPackages</source>
        <translation>GPKG Merger – 合并 GeoPackage</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="89"/>
        <source>1. Input GeoPackages (merge order: top → bottom)</source>
        <translation>1. 输入 GeoPackage（合并顺序：从上到下）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="92"/>
        <source>Drag items to change the merge order. You can also drop .gpkg files here.</source>
        <translation>拖动项目可调整合并顺序，也可将 .gpkg 文件直接拖放到这里。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="96"/>
        <source>Add…</source>
        <translation>添加…</translation>
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
        <translation>2. 图层与结果预览</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="125"/>
        <source>3. Layers with the same name</source>
        <translation>3. 同名图层处理方式</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="127"/>
        <source>Keep all – rename to &lt;gpkg name&gt;_&lt;layer name&gt;</source>
        <translation>不覆盖 – 全部保留并改名为 &lt;gpkg名称&gt;_&lt;图层名称&gt;</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="128"/>
        <source>Overwrite – a later file replaces earlier ones</source>
        <translation>覆盖 – 按合并顺序，后面的文件覆盖前面的</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="129"/>
        <source>Append – merge features into one layer (geometry type, CRS and fields must match)</source>
        <translation>扩充 – 将要素并入同一图层（几何类型、坐标系与字段须一致）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="138"/>
        <source>4. Output</source>
        <translation>4. 输出</translation>
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
        <translation>输出 GeoPackage</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="146"/>
        <source>Copy QGIS layer styles (layer_styles table)</source>
        <translation>一并复制 QGIS 图层样式（layer_styles 表）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="148"/>
        <source>Add merged layers to the project</source>
        <translation>将合并后的图层加入项目</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="170"/>
        <source>Merge</source>
        <translation>合并</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="172"/>
        <source>Cancel</source>
        <translation>取消</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="174"/>
        <source>Close</source>
        <translation>关闭</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="224"/>
        <source>Select GeoPackages</source>
        <translation>选择 GeoPackage</translation>
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
        <translation>图层</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="111"/>
        <source>Geometry</source>
        <translation>几何</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="111"/>
        <source>CRS</source>
        <translation>坐标系</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="112"/>
        <source>Features</source>
        <translation>要素数</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="112"/>
        <source>Result</source>
        <translation>结果</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="292"/>
        <location filename="../dialog.py" line="384"/>
        <source>Add at least two GeoPackages to merge.</source>
        <translation>请至少添加两个 GeoPackage 才能合并。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="351"/>
        <source>Append is not possible – change the order, remove files or choose another option.</source>
        <translation>无法扩充 – 请调整顺序、移除文件或改选其他方式。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="389"/>
        <source>Please choose an output file.</source>
        <translation>请选择输出文件。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="397"/>
        <location filename="../merge_core.py" line="373"/>
        <source>The output file must not be one of the input files.</source>
        <translation>输出文件不能与输入文件相同。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="412"/>
        <source>Merge stopped:</source>
        <translation>合并已停止：</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="416"/>
        <source>Layers cannot be appended</source>
        <translation>图层无法扩充</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="348"/>
        <source>{0} files, {1} output layers, {2} duplicate layer names.</source>
        <translation>{0} 个文件，输出 {1} 个图层，{2} 个重复图层名称。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="444"/>
        <source>Cancelled. No output was written.</source>
        <translation>已取消，未写入任何输出。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="458"/>
        <source>{0} layers written to {1}</source>
        <translation>已写入 {0} 个图层至 {1}</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="306"/>
        <source>copy</source>
        <translation>复制</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="325"/>
        <source>INCOMPATIBLE – cannot append</source>
        <translation>格式不符 – 无法扩充</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="339"/>
        <source>This layer name exists in more than one file.</source>
        <translation>此图层名称出现在多个文件中。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="417"/>
        <source>The following layers have a different structure and cannot be appended. Nothing was written.

Change the merge order, remove files or choose another option, then try again.</source>
        <translation>下列图层的矢量格式不一致，无法扩充，未写入任何数据。

请调整合并顺序、移除文件或改选其他处理方式后再试一次。</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="426"/>
        <source>The file already exists:
{0}

Replace it?</source>
        <translation>文件已存在：
{0}

要替换吗？</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="302"/>
        <source>append to '{0}'</source>
        <translation>扩充至“{0}”</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="329"/>
        <source>dropped (overwritten by a later file)</source>
        <translation>舍弃（被后面的文件覆盖）</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="448"/>
        <location filename="../dialog.py" line="449"/>
        <source>Error: {0}</source>
        <translation>错误：{0}</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="482"/>
        <source>Could not load layer '{0}'</source>
        <translation>无法加载图层“{0}”</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="304"/>
        <source>rename to '{0}'</source>
        <translation>改名为“{0}”</translation>
    </message>
    <message>
        <location filename="../dialog.py" line="342"/>
        <source>skipped: {0}</source>
        <translation>跳过：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="105"/>
        <source>No geometry</source>
        <translation>无几何</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="366"/>
        <source>The merge plan contains errors; nothing was written.</source>
        <translation>合并计划有错误，未写入任何数据。</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="368"/>
        <source>There is nothing to merge.</source>
        <translation>没有可合并的图层。</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="457"/>
        <source>Done: {0}</source>
        <translation>完成：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="244"/>
        <source>geometry type differs ({0} vs {1})</source>
        <translation>几何类型不同（{0} 与 {1}）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="249"/>
        <location filename="../merge_core.py" line="252"/>
        <source>coordinate reference system differs ({0} vs {1})</source>
        <translation>坐标系不同（{0} 与 {1}）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="250"/>
        <location filename="../merge_core.py" line="250"/>
        <source>none</source>
        <translation>无</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="260"/>
        <source>missing fields: {0}</source>
        <translation>缺少字段：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="262"/>
        <source>extra fields: {0}</source>
        <translation>多出字段：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="174"/>
        <location filename="../merge_core.py" line="172"/>
        <source>Cannot open GeoPackage: {0}</source>
        <translation>无法打开 GeoPackage：{0}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="196"/>
        <source>QGIS project storage table is not merged</source>
        <translation>QGIS 项目存储表不合并</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="265"/>
        <source>field '{0}' type differs ({1} vs {2})</source>
        <translation>字段“{0}”类型不同（{1} 与 {2}）</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="351"/>
        <source>Skipped '{0}' in '{1}': {2}</source>
        <translation>跳过“{1}”中的“{0}”：{2}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="183"/>
        <source>raster/tiles table is not supported</source>
        <translation>不支持栅格/瓦片数据表</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="321"/>
        <source>Layer '{0}' of '{1}' renamed to '{2}'</source>
        <translation>“{1}”的图层“{0}”改名为“{2}”</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="437"/>
        <source>Copying layer styles from '{0}'</source>
        <translation>复制“{0}”的图层样式</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="329"/>
        <source>Layer '{0}' of '{1}' is overwritten by '{2}'</source>
        <translation>“{1}”的图层“{0}”被“{2}”覆盖</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="410"/>
        <source>Copying '{0}' from '{1}' as '{2}'</source>
        <translation>复制“{1}”的“{0}”为“{2}”</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="421"/>
        <source>Appending '{0}' from '{1}' to '{2}'</source>
        <translation>将“{1}”的“{0}”扩充至“{2}”</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="341"/>
        <source>Layer '{0}': '{1}' cannot be appended to '{2}': {3}</source>
        <translation>图层“{0}”：“{1}”无法扩充至“{2}”：{3}</translation>
    </message>
    <message>
        <location filename="../merge_core.py" line="346"/>
        <source>{0} features of '{1}' in '{2}' appended to layer '{3}'</source>
        <translation>“{2}”中“{1}”的 {0} 个要素扩充至图层“{3}”</translation>
    </message>
    <message>
        <location filename="../plugin.py" line="58"/>
        <source>Merge GeoPackages…</source>
        <translation>合并 GeoPackage…</translation>
    </message>
    <message>
        <location filename="../plugin.py" line="59"/>
        <source>Merge several GeoPackage files into one</source>
        <translation>将多个 GeoPackage 文件合并为一个</translation>
    </message>
    <message>
        <location filename="../plugin.py" line="61"/>
        <location filename="../plugin.py" line="66"/>
        <source>&amp;GPKG Merger</source>
        <translation>&amp;GPKG Merger</translation>
    </message>
</context>
</TS>
