# -*- coding: utf-8 -*-
"""Main dialog of GPKG Merger (Qt5 / Qt6 compatible through qgis.PyQt)."""

import os

from qgis.core import QgsProject, QgsSettings, QgsVectorLayer
from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QBrush, QColor
from qgis.PyQt.QtWidgets import (
    QAbstractItemView, QApplication, QButtonGroup, QCheckBox, QDialog,
    QFileDialog, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QListWidget,
    QListWidgetItem, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton,
    QRadioButton, QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget,
)

from . import merge_core as mc
from .i18n_util import tr

SETTINGS_PREFIX = "gpkg_merger/"
COLOR_CONFLICT = QColor(230, 140, 0)
COLOR_ERROR = QColor(200, 30, 30)
COLOR_DROPPED = QColor(140, 140, 140)


class FileListWidget(QListWidget):
    """List that can be re-ordered by drag & drop and accepts .gpkg files
    dropped from the file manager."""
    filesDropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super(FileListWidget, self).__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAcceptDrops(True)

    @staticmethod
    def _gpkg_urls(event):
        md = event.mimeData()
        if not md.hasUrls():
            return []
        return [u.toLocalFile() for u in md.urls()
                if u.isLocalFile() and u.toLocalFile().lower().endswith(".gpkg")]

    def dragEnterEvent(self, event):  # noqa: N802
        if self._gpkg_urls(event):
            event.acceptProposedAction()
        else:
            super(FileListWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(FileListWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):  # noqa: N802
        files = self._gpkg_urls(event)
        if files:
            event.acceptProposedAction()
            self.filesDropped.emit(files)
        else:
            super(FileListWidget, self).dropEvent(event)


class GpkgMergerDialog(QDialog):
    def __init__(self, iface, parent=None):
        super(GpkgMergerDialog, self).__init__(parent)
        self.iface = iface
        self._cache = {}          # path -> SourceInfo
        self._plan = None
        self._running = False
        self._cancel = False
        self.setWindowTitle(tr("GPKG Merger – merge GeoPackages"))
        self.resize(920, 780)
        self._build_ui()
        self._restore_settings()
        self._refresh()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        root = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Vertical)
        root.addWidget(splitter, 1)

        # 1. input files
        box_in = QGroupBox(tr("1. Input GeoPackages (merge order: top → bottom)"))
        lay_in = QHBoxLayout(box_in)
        self.list_files = FileListWidget()
        self.list_files.setToolTip(tr("Drag items to change the merge order. "
                                      "You can also drop .gpkg files here."))
        lay_in.addWidget(self.list_files, 1)
        btns = QVBoxLayout()
        self.btn_add = QPushButton(tr("Add…"))
        self.btn_remove = QPushButton(tr("Remove"))
        self.btn_up = QPushButton(tr("Move up"))
        self.btn_down = QPushButton(tr("Move down"))
        self.btn_clear = QPushButton(tr("Clear"))
        for b in (self.btn_add, self.btn_remove, self.btn_up, self.btn_down, self.btn_clear):
            btns.addWidget(b)
        btns.addStretch(1)
        lay_in.addLayout(btns)
        splitter.addWidget(box_in)

        # 2. layer preview
        box_layers = QGroupBox(tr("2. Layers and result preview"))
        lay_layers = QVBoxLayout(box_layers)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([tr("Layer"), tr("Geometry"), tr("CRS"),
                                   tr("Features"), tr("Result")])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setStretchLastSection(True)
        lay_layers.addWidget(self.tree)
        self.lbl_summary = QLabel()
        self.lbl_summary.setWordWrap(True)
        lay_layers.addWidget(self.lbl_summary)
        splitter.addWidget(box_layers)

        # 3 + 4 options
        opts = QWidget()
        lay_opts = QHBoxLayout(opts)
        lay_opts.setContentsMargins(0, 0, 0, 0)
        box_mode = QGroupBox(tr("3. Layers with the same name"))
        lay_mode = QVBoxLayout(box_mode)
        self.rb_rename = QRadioButton(tr("Keep all – rename to <gpkg name>_<layer name>"))
        self.rb_overwrite = QRadioButton(tr("Overwrite – a later file replaces earlier ones"))
        self.rb_append = QRadioButton(tr("Append – merge features into one layer "
                                         "(geometry type, CRS and fields must match)"))
        self.mode_group = QButtonGroup(self)
        for rb in (self.rb_rename, self.rb_overwrite, self.rb_append):
            self.mode_group.addButton(rb)
            lay_mode.addWidget(rb)
        self.rb_rename.setChecked(True)
        lay_opts.addWidget(box_mode, 1)

        box_out = QGroupBox(tr("4. Output"))
        lay_out = QVBoxLayout(box_out)
        self.file_out = QgsFileWidget()
        self.file_out.setStorageMode(QgsFileWidget.StorageMode.SaveFile)
        self.file_out.setFilter(tr("GeoPackage (*.gpkg)"))
        self.file_out.setDialogTitle(tr("Output GeoPackage"))
        self.file_out.setConfirmOverwrite(False)  # asked when merging
        lay_out.addWidget(self.file_out)
        self.chk_styles = QCheckBox(tr("Copy QGIS layer styles (layer_styles table)"))
        self.chk_styles.setChecked(True)
        self.chk_load = QCheckBox(tr("Add merged layers to the project"))
        self.chk_load.setChecked(True)
        lay_out.addWidget(self.chk_styles)
        lay_out.addWidget(self.chk_load)
        lay_out.addStretch(1)
        lay_opts.addWidget(box_out, 1)
        splitter.addWidget(opts)

        # log
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(5000)
        splitter.addWidget(self.log)
        splitter.setSizes([140, 320, 120, 100])

        # bottom row
        bottom = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        bottom.addWidget(self.progress, 1)
        self.btn_run = QPushButton(tr("Merge"))
        self.btn_run.setDefault(True)
        self.btn_cancel = QPushButton(tr("Cancel"))
        self.btn_cancel.setEnabled(False)
        self.btn_close = QPushButton(tr("Close"))
        bottom.addWidget(self.btn_run)
        bottom.addWidget(self.btn_cancel)
        bottom.addWidget(self.btn_close)
        root.addLayout(bottom)

        # signals
        self.btn_add.clicked.connect(self._add_dialog)
        self.btn_remove.clicked.connect(self._remove_selected)
        self.btn_up.clicked.connect(lambda: self._move(-1))
        self.btn_down.clicked.connect(lambda: self._move(1))
        self.btn_clear.clicked.connect(self._clear)
        self.list_files.filesDropped.connect(self._add_files)
        self.list_files.model().rowsMoved.connect(lambda *a: self._refresh())
        self.mode_group.buttonClicked.connect(lambda *a: self._refresh())
        self.btn_run.clicked.connect(self._run)
        self.btn_cancel.clicked.connect(self._request_cancel)
        self.btn_close.clicked.connect(self.close)

    # ------------------------------------------------------------ settings
    def _restore_settings(self):
        s = QgsSettings()
        mode = s.value(SETTINGS_PREFIX + "mode", mc.MODE_RENAME, type=str)
        {mc.MODE_OVERWRITE: self.rb_overwrite,
         mc.MODE_APPEND: self.rb_append}.get(mode, self.rb_rename).setChecked(True)
        self.chk_styles.setChecked(s.value(SETTINGS_PREFIX + "copyStyles", True, type=bool))
        self.chk_load.setChecked(s.value(SETTINGS_PREFIX + "addToProject", True, type=bool))

    def _save_settings(self):
        s = QgsSettings()
        s.setValue(SETTINGS_PREFIX + "mode", self.mode())
        s.setValue(SETTINGS_PREFIX + "copyStyles", self.chk_styles.isChecked())
        s.setValue(SETTINGS_PREFIX + "addToProject", self.chk_load.isChecked())

    def mode(self):
        if self.rb_overwrite.isChecked():
            return mc.MODE_OVERWRITE
        if self.rb_append.isChecked():
            return mc.MODE_APPEND
        return mc.MODE_RENAME

    # -------------------------------------------------------------- files
    def paths(self):
        return [self.list_files.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.list_files.count())]

    def _add_dialog(self):
        s = QgsSettings()
        start = s.value(SETTINGS_PREFIX + "lastDir", "", type=str)
        files, _ = QFileDialog.getOpenFileNames(
            self, tr("Select GeoPackages"), start, tr("GeoPackage (*.gpkg)"))
        if files:
            s.setValue(SETTINGS_PREFIX + "lastDir", os.path.dirname(files[0]))
            self._add_files(files)

    def _add_files(self, files):
        existing = {os.path.normcase(os.path.abspath(p)) for p in self.paths()}
        failed = []
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            for f in files:
                key = os.path.normcase(os.path.abspath(f))
                if key in existing:
                    continue
                try:
                    self._cache[f] = mc.scan_gpkg(f)
                except mc.MergeError as e:
                    failed.append(str(e))
                    continue
                existing.add(key)
                item = QListWidgetItem(os.path.basename(f))
                item.setToolTip(f)
                item.setData(Qt.ItemDataRole.UserRole, f)
                self.list_files.addItem(item)
        finally:
            QApplication.restoreOverrideCursor()
        if failed:
            QMessageBox.warning(self, tr("GPKG Merger"), "\n\n".join(failed))
        if not self.file_out.filePath() and self.list_files.count():
            first = self.paths()[0]
            self.file_out.setFilePath(os.path.join(os.path.dirname(first), "merged.gpkg"))
        self._refresh()

    def _remove_selected(self):
        for item in self.list_files.selectedItems():
            self.list_files.takeItem(self.list_files.row(item))
        self._refresh()

    def _clear(self):
        self.list_files.clear()
        self._refresh()

    def _move(self, delta):
        rows = sorted(self.list_files.row(i) for i in self.list_files.selectedItems())
        if not rows:
            return
        if delta < 0 and rows[0] == 0:
            return
        if delta > 0 and rows[-1] == self.list_files.count() - 1:
            return
        order = rows if delta < 0 else list(reversed(rows))
        for r in order:
            item = self.list_files.takeItem(r)
            self.list_files.insertItem(r + delta, item)
        self.list_files.clearSelection()
        for r in rows:
            self.list_files.item(r + delta).setSelected(True)
        self._refresh()

    # ------------------------------------------------------------ preview
    def _sources(self):
        return [self._cache[p] for p in self.paths()]

    def _refresh(self):
        sources = self._sources()
        self._plan = mc.build_plan(sources, self.mode()) if sources else None
        self.tree.clear()
        if not sources:
            self.lbl_summary.setText(tr("Add at least two GeoPackages to merge."))
            return

        plan = self._plan
        conflicts = mc.find_conflicts(sources)
        # result text per (source index, layer)
        result = {}
        for st in plan.steps:
            key = (st.source_index, st.src_layer)
            if st.action == mc.Step.APPEND:
                result[key] = (tr("append to '{0}'").format(st.out_name), None)
            elif st.out_name != st.src_layer:
                result[key] = (tr("rename to '{0}'").format(st.out_name), None)
            else:
                result[key] = (tr("copy"), None)
        error_layers = set()
        if plan.mode == mc.MODE_APPEND:
            for key, occ in conflicts.items():
                base = occ[0][1]
                for si, lyr in occ[1:]:
                    if mc.check_compatible(base, lyr):
                        error_layers.add((si, lyr.name))

        for si, src in enumerate(sources):
            top = QTreeWidgetItem([u"{0}. {1}".format(si + 1, os.path.basename(src.path))])
            top.setToolTip(0, src.path)
            f = top.font(0)
            f.setBold(True)
            top.setFont(0, f)
            self.tree.addTopLevelItem(top)
            for lyr in src.layers:
                key = (si, lyr.name)
                if key in error_layers:
                    text, color = tr("INCOMPATIBLE – cannot append"), COLOR_ERROR
                elif key in result:
                    text, color = result[key][0], None
                else:
                    text, color = tr("dropped (overwritten by a later file)"), COLOR_DROPPED
                is_conflict = lyr.name.lower() in conflicts
                if is_conflict and color is None:
                    color = COLOR_CONFLICT
                child = QTreeWidgetItem([lyr.name, lyr.geom_type_name, lyr.srs_name,
                                         str(lyr.feature_count), text])
                if color is not None:
                    for c in range(5):
                        child.setForeground(c, QBrush(color))
                if is_conflict:
                    child.setToolTip(0, tr("This layer name exists in more than one file."))
                top.addChild(child)
            for name, reason in src.skipped:
                child = QTreeWidgetItem([name, "", "", "", tr("skipped: {0}").format(reason)])
                for c in range(5):
                    child.setForeground(c, QBrush(COLOR_DROPPED))
                top.addChild(child)
            top.setExpanded(True)

        parts = [tr("{0} files, {1} output layers, {2} duplicate layer names.").format(
            len(sources), len(plan.output_layers), len(conflicts))]
        if plan.errors:
            parts.append(tr("Append is not possible – change the order, remove files or "
                            "choose another option."))
        self.lbl_summary.setText(" ".join(parts))
        pal_color = COLOR_ERROR.name() if plan.errors else ""
        self.lbl_summary.setStyleSheet("color: %s;" % pal_color if pal_color else "")

    # ---------------------------------------------------------------- run
    def _log(self, msg):
        self.log.appendPlainText(msg)
        QApplication.processEvents()

    def _progress(self, frac):
        self.progress.setValue(int(frac * 1000))
        QApplication.processEvents()
        return not self._cancel

    def _request_cancel(self):
        self._cancel = True
        self.btn_cancel.setEnabled(False)

    def _set_running(self, running):
        self._running = running
        for w in (self.btn_run, self.btn_close, self.btn_add, self.btn_remove,
                  self.btn_up, self.btn_down, self.btn_clear, self.list_files,
                  self.rb_rename, self.rb_overwrite, self.rb_append,
                  self.file_out, self.chk_styles, self.chk_load):
            w.setEnabled(not running)
        self.btn_cancel.setEnabled(running)

    def _run(self):
        paths = self.paths()
        if len(paths) < 2:
            QMessageBox.information(self, tr("GPKG Merger"),
                                    tr("Add at least two GeoPackages to merge."))
            return
        out = self.file_out.filePath().strip()
        if not out:
            QMessageBox.information(self, tr("GPKG Merger"),
                                    tr("Please choose an output file."))
            return
        if not out.lower().endswith(".gpkg"):
            out += ".gpkg"
            self.file_out.setFilePath(out)
        out_key = os.path.normcase(os.path.abspath(out))
        if out_key in {os.path.normcase(os.path.abspath(p)) for p in paths}:
            QMessageBox.warning(self, tr("GPKG Merger"),
                                tr("The output file must not be one of the input files."))
            return

        # re-scan in case the files changed since they were added
        try:
            for p in paths:
                self._cache[p] = mc.scan_gpkg(p)
        except mc.MergeError as e:
            QMessageBox.warning(self, tr("GPKG Merger"), str(e))
            return
        self._refresh()
        plan = self._plan

        if not plan.ok:
            # Append mode with incompatible layers: stop, let the user re-select.
            self.log.appendPlainText(tr("Merge stopped:"))
            for err in plan.errors:
                self.log.appendPlainText("  ✗ " + err)
            QMessageBox.warning(
                self, tr("Layers cannot be appended"),
                tr("The following layers have a different structure and cannot be "
                   "appended. Nothing was written.\n\nChange the merge order, remove "
                   "files or choose another option, then try again.") +
                "\n\n" + "\n".join(u"• " + e for e in plan.errors))
            return

        if os.path.exists(out):
            ans = QMessageBox.question(
                self, tr("GPKG Merger"),
                tr("The file already exists:\n{0}\n\nReplace it?").format(out),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if ans != QMessageBox.StandardButton.Yes:
                return
            self._remove_project_layers(out)

        self._save_settings()
        self.log.clear()
        for note in plan.notes:
            self.log.appendPlainText("• " + note)
        self._cancel = False
        self._set_running(True)
        self.progress.setValue(0)
        try:
            layers = mc.execute_plan(plan, out, copy_styles=self.chk_styles.isChecked(),
                                     progress=self._progress, log=self._log)
        except mc.MergeCancelled:
            self._log(tr("Cancelled. No output was written."))
            self.progress.setValue(0)
            return
        except mc.MergeError as e:
            self._log(tr("Error: {0}").format(e))
            QMessageBox.critical(self, tr("GPKG Merger"), tr("Error: {0}").format(e))
            return
        finally:
            self._set_running(False)

        if self.chk_load.isChecked():
            self._load_result(out, layers)
        self.iface.messageBar().pushSuccess(
            tr("GPKG Merger"),
            tr("{0} layers written to {1}").format(len(layers), out))

    def _remove_project_layers(self, path):
        """Remove layers of a file we are going to replace, so it is not locked."""
        key = os.path.normcase(os.path.abspath(path))
        proj = QgsProject.instance()
        ids = []
        for lid, layer in proj.mapLayers().items():
            src = layer.source().split("|")[0]
            if os.path.normcase(os.path.abspath(src)) == key:
                ids.append(lid)
        if ids:
            proj.removeMapLayers(ids)

    def _load_result(self, path, layers):
        proj = QgsProject.instance()
        root = proj.layerTreeRoot()
        group = root.insertGroup(0, os.path.splitext(os.path.basename(path))[0])
        for name in layers:
            vl = QgsVectorLayer(u"{0}|layername={1}".format(path, name), name, "ogr")
            if vl.isValid():
                proj.addMapLayer(vl, False)
                group.addLayer(vl)
            else:
                self._log(tr("Could not load layer '{0}'").format(name))

    def closeEvent(self, event):  # noqa: N802
        if self._running:
            event.ignore()
            return
        self._save_settings()
        super(GpkgMergerDialog, self).closeEvent(event)
