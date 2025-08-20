from PyQt6 import QtWidgets
from ui import Ui_MainWindow
import sys
import time
import shutil
import os
from PyQt6.QtCore import QFileSystemWatcher


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.backup = ""
        self.path_to_save = ""
        self.path_to_dir = ""
        self.watcher = None
        self.is_watching = False
        self.ignore_next_change = False

        self.file_pick_button.clicked.connect(self.pick_file)
        self.start_button.clicked.connect(self.on_start)
        self.backup_button.clicked.connect(self.on_backup)
        self.save_picker_combo_box.currentIndexChanged.connect(
            self.on_combo_change)

    def pick_file(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "Выберите файл сохранения")
        if file_path:
            self.path_to_save_line_edit.setText(file_path)
            self.statusBar.showMessage(f"Файл выбран: {file_path}")
            self.save_picker_combo_box.clear()

            dir_path = os.path.dirname(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            added = set()
            for fname in os.listdir(dir_path):
                if fname.startswith(base_name) and fname.endswith(".chzback"):
                    if fname not in added:
                        self.save_picker_combo_box.addItem(fname)
                        added.add(fname)

    def on_start(self):
        self.path_to_save = self.path_to_save_line_edit.text()
        if self.path_to_save.endswith(".hoi4"):
            self.statusBar.showMessage("Работаем парни")
            self.path_to_dir = os.path.dirname(self.path_to_save)
            self.create_backup()

            if self.watcher:
                self.watcher.fileChanged.disconnect()
                del self.watcher
            self.watcher = QFileSystemWatcher([self.path_to_save])
            self.watcher.fileChanged.connect(self.on_file_changed)
            self.is_watching = True

            self.start_button.setText("Стоп")
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self.on_stop)
        else:
            self.statusBar.showMessage("Неверный формат файла")

    def on_stop(self):
        if self.watcher:
            self.watcher.fileChanged.disconnect()
            del self.watcher
            self.watcher = None
        self.is_watching = False
        self.statusBar.showMessage("Отслеживание остановлено")

        # Меняем кнопку Stop обратно на Start
        self.start_button.setText("Старт")
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.on_start)

    def create_backup(self):
        base_name = os.path.splitext(os.path.basename(self.path_to_save))[0]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        new_filename = f"{base_name}_{timestamp}.chzback"
        new_path = os.path.join(self.path_to_dir, new_filename)
        try:
            shutil.copy2(self.path_to_save, new_path)
            self.statusBar.showMessage(f"Сохранено: {new_path}")
            self.save_picker_combo_box.addItem(new_filename)
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка копирования: {e}")

    def on_file_changed(self, path):
        if self.ignore_next_change:
            self.ignore_next_change = False
            return

        if os.path.exists(path):
            self.create_backup()

    def on_backup(self):
        selected_backup = self.save_picker_combo_box.currentText()
        if not selected_backup:
            self.statusBar.showMessage("Не выбран файл для восстановления")
            return

        if not self.path_to_save:
            self.statusBar.showMessage(
                "Не выбран исходный файл для восстановления")
            return

        backup_path = os.path.join(self.path_to_dir, selected_backup)

        original_filename = os.path.basename(self.path_to_save)
        restore_path = os.path.join(self.path_to_dir, original_filename)

        try:
            self.ignore_next_change = True
            shutil.copy2(backup_path, restore_path)
            self.statusBar.showMessage(f"Восстановлено как: {restore_path}")
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка восстановления: {e}")

    def on_combo_change(self, index):
        self.backup = self.save_picker_combo_box.itemText(index)
        self.statusBar.showMessage(f"Выбран: {self.backup}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
