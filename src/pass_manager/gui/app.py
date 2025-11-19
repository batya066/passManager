from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWidgets import QAbstractItemView, QHeaderView

from ..exceptions import EntryNotFound, VaultError
from ..models import Vault, VaultEntry
from ..passwords import GeneratorOptions, SYMBOL_SETS, generate_password
from ..storage import DEFAULT_VAULT_PATH, SecureVault, VaultStorage


def _parse_tags(text: str) -> List[str]:
    return [tag.strip() for tag in text.split(",") if tag.strip()]


@dataclass
class UnlockResult:
    vault_path: str
    master_password: str
    create_new: bool


class UnlockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kasayı Aç / Oluştur")
        self._result: Optional[UnlockResult] = None

        layout = QVBoxLayout(self)
        form = QFormLayout()

        path_row = QHBoxLayout()
        self.path_edit = QLineEdit(str(DEFAULT_VAULT_PATH))
        browse_button = QPushButton("Seç")
        browse_button.clicked.connect(self._browse_path)
        path_row.addWidget(self.path_edit)
        path_row.addWidget(browse_button)
        form.addRow("Kasa Dosyası", path_row)

        self.create_checkbox = QCheckBox("Yeni kasa oluştur")
        self.create_checkbox.toggled.connect(self._toggle_create)
        form.addRow("", self.create_checkbox)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Ana Parola", self.password_edit)

        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Ana Parola (tekrar)", self.confirm_edit)
        self.confirm_edit.hide()

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._handle_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _toggle_create(self, checked: bool) -> None:
        self.confirm_edit.setVisible(checked)

    def _browse_path(self) -> None:
        caption = "Kasa dosyasını seç"
        path, _ = QFileDialog.getSaveFileName(self, caption, self.path_edit.text())
        if path:
            self.path_edit.setText(path)

    def _handle_accept(self) -> None:
        path = self.path_edit.text().strip()
        password = self.password_edit.text().strip()
        create_new = self.create_checkbox.isChecked()
        if not path:
            QMessageBox.warning(self, "Eksik Bilgi", "Kasa dosyası yolunu belirtmelisiniz.")
            return
        if len(password) < 8:
            QMessageBox.warning(self, "Zayıf Parola", "Ana parola en az 8 karakter olmalıdır.")
            return
        if create_new:
            confirm = self.confirm_edit.text().strip()
            if password != confirm:
                QMessageBox.warning(self, "Parolalar Eşleşmiyor", "Ana parolayı iki kez aynı girin.")
                return
        self._result = UnlockResult(path, password, create_new)
        self.accept()

    def get_result(self) -> Optional[UnlockResult]:
        return self._result


class EntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Kayıt")
        self._data: Optional[dict] = None

        main_layout = QVBoxLayout(self)
        form = QFormLayout()

        self.service_edit = QLineEdit()
        form.addRow("Servis", self.service_edit)

        self.username_edit = QLineEdit()
        form.addRow("Kullanıcı Adı", self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Parola", self.password_edit)

        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("virgülle ayrılmış etiketler")
        form.addRow("Etiketler", self.tags_edit)

        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlaceholderText("isteğe bağlı not")
        form.addRow("Notlar", self.notes_edit)

        main_layout.addLayout(form)

        generator_box = QGroupBox("Parola üretici")
        gen_layout = QHBoxLayout()
        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 128)
        self.length_spin.setValue(24)
        self.symbol_combo = QComboBox()
        for key in SYMBOL_SETS.keys():
            self.symbol_combo.addItem(key, userData=key)
        self.allow_ambiguous = QCheckBox("Benzeyen karakterlere izin ver")
        self.require_each = QCheckBox("Her gruptan karakter zorunlu")
        self.require_each.setChecked(True)
        generate_button = QPushButton("Parola üret")
        generate_button.clicked.connect(self._generate_password)

        gen_layout.addWidget(QLabel("Uzunluk"))
        gen_layout.addWidget(self.length_spin)
        gen_layout.addWidget(QLabel("Semboller"))
        gen_layout.addWidget(self.symbol_combo)
        gen_layout.addWidget(self.allow_ambiguous)
        gen_layout.addWidget(self.require_each)
        gen_layout.addWidget(generate_button)
        generator_box.setLayout(gen_layout)
        main_layout.addWidget(generator_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._handle_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def _generate_password(self) -> None:
        options = GeneratorOptions(
            length=self.length_spin.value(),
            symbols=self.symbol_combo.currentData(),
            allow_ambiguous=self.allow_ambiguous.isChecked(),
            require_each_category=self.require_each.isChecked(),
        )
        password = generate_password(options)
        self.password_edit.setText(password)
        self.password_edit.setEchoMode(QLineEdit.Normal)

    def _handle_accept(self) -> None:
        service = self.service_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not service or not username:
            QMessageBox.warning(self, "Eksik Bilgi", "Servis ve kullanıcı adı zorunlu.")
            return
        if len(password) < 6:
            QMessageBox.warning(self, "Zayıf Parola", "Parola en az 6 karakter olmalı.")
            return
        self._data = {
            "service": service,
            "username": username,
            "password": password,
            "notes": self.notes_edit.toPlainText().strip(),
            "tags": _parse_tags(self.tags_edit.text()),
        }
        self.accept()

    def get_data(self) -> Optional[dict]:
        return self._data


class PasswordGeneratorDialog(QDialog):
    def __init__(self, clipboard_guard: "ClipboardGuard", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parola Üret")
        self.clipboard_guard = clipboard_guard

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 128)
        self.length_spin.setValue(28)
        form.addRow("Uzunluk", self.length_spin)

        self.symbol_combo = QComboBox()
        for key in SYMBOL_SETS.keys():
            self.symbol_combo.addItem(key, userData=key)
        self.symbol_combo.setCurrentText("hard")
        form.addRow("Sembol modu", self.symbol_combo)

        self.allow_ambiguous = QCheckBox("Benzeyen karakterleri dahil et")
        form.addRow("", self.allow_ambiguous)

        self.require_each = QCheckBox("Her karakter grubundan en az bir tane kullan")
        self.require_each.setChecked(True)
        form.addRow("", self.require_each)

        layout.addLayout(form)

        self.result_edit = QLineEdit()
        self.result_edit.setReadOnly(True)
        self.result_edit.setPlaceholderText("Parola üretildiğinde burada görünecek")
        layout.addWidget(self.result_edit)

        button_row = QHBoxLayout()
        generate_button = QPushButton("Üret")
        generate_button.clicked.connect(self._generate)
        copy_button = QPushButton("Panoya kopyala")
        copy_button.clicked.connect(self._copy)
        button_row.addWidget(generate_button)
        button_row.addWidget(copy_button)
        layout.addLayout(button_row)

        close_buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_buttons.rejected.connect(self.reject)
        close_buttons.accepted.connect(self.accept)
        layout.addWidget(close_buttons)

    def _generate(self) -> None:
        options = GeneratorOptions(
            length=self.length_spin.value(),
            symbols=self.symbol_combo.currentData(),
            allow_ambiguous=self.allow_ambiguous.isChecked(),
            require_each_category=self.require_each.isChecked(),
        )
        password = generate_password(options)
        self.result_edit.setText(password)

    def _copy(self) -> None:
        password = self.result_edit.text()
        if password:
            self.clipboard_guard.copy(password)
            QMessageBox.information(self, "Panoya Kopyalandı", "Parola 30 sn içinde otomatik temizlenecek.")


class ClipboardGuard(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.timer = QTimer(self)
        self.timer.setInterval(30_000)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clear)

    def copy(self, text: str) -> None:
        clipboard = self.app.clipboard()
        clipboard.setText(text, mode=clipboard.Clipboard)
        self.timer.start()

    def clear(self) -> None:
        clipboard = self.app.clipboard()
        clipboard.clear(mode=clipboard.Clipboard)


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.clipboard_guard = ClipboardGuard(app)
        self.secure_vault: Optional[SecureVault] = None
        self.master_password: Optional[str] = None
        self.vault: Optional[Vault] = None
        self.current_entry: Optional[VaultEntry] = None
        self.password_visible = False
        self.initialized = False

        self.setWindowTitle("Kişiye Özel Şifre Kasası (GUI)")
        self.resize(1100, 720)
        self.statusBar().showMessage("Kasa yükleniyor...")

        result = request_vault(self)
        if result is None:
            return
        self.secure_vault, self.master_password, self.vault = result
        self.initialized = True
        self._build_ui()
        self.load_entries()
        self.statusBar().showMessage("Kasa hazır.")

    def _build_ui(self) -> None:
        central = QWidget()
        main_layout = QVBoxLayout(central)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Servis", "Kullanıcı", "Etiketler", "Güncellendi"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.itemSelectionChanged.connect(self.display_selected_entry)
        main_layout.addWidget(self.table)

        button_row = QHBoxLayout()
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.load_entries)
        add_btn = QPushButton("Kayıt Ekle")
        add_btn.clicked.connect(self.add_entry)
        delete_btn = QPushButton("Kayıt Sil")
        delete_btn.clicked.connect(self.delete_entry)
        generator_btn = QPushButton("Parola Üret")
        generator_btn.clicked.connect(self.open_generator)
        lock_btn = QPushButton("Kilitle / Kasa Değiştir")
        lock_btn.clicked.connect(self.relock_vault)
        button_row.addWidget(refresh_btn)
        button_row.addWidget(add_btn)
        button_row.addWidget(delete_btn)
        button_row.addWidget(generator_btn)
        button_row.addWidget(lock_btn)
        button_row.addStretch()
        main_layout.addLayout(button_row)

        detail_box = QGroupBox("Kayıt Detayı")
        detail_layout = QFormLayout()
        self.service_label = QLabel("-")
        self.username_label = QLabel("-")
        self.tags_label = QLabel("-")
        self.created_label = QLabel("-")
        self.updated_label = QLabel("-")

        self.password_field = QLineEdit()
        self.password_field.setReadOnly(True)
        self.password_field.setEchoMode(QLineEdit.Password)

        password_buttons = QHBoxLayout()
        password_buttons.addWidget(self.password_field)
        self.reveal_button = QPushButton("Göster")
        self.reveal_button.clicked.connect(self.toggle_password_visibility)
        self.copy_button = QPushButton("Panoya kopyala")
        self.copy_button.clicked.connect(self.copy_password)
        password_buttons.addWidget(self.reveal_button)
        password_buttons.addWidget(self.copy_button)

        self.notes_view = QPlainTextEdit()
        self.notes_view.setReadOnly(True)
        self.notes_view.setMaximumBlockCount(200)

        detail_layout.addRow("Servis", self.service_label)
        detail_layout.addRow("Kullanıcı", self.username_label)
        detail_layout.addRow("Parola", password_buttons)
        detail_layout.addRow("Etiketler", self.tags_label)
        detail_layout.addRow("Notlar", self.notes_view)
        detail_layout.addRow("Oluşturuldu", self.created_label)
        detail_layout.addRow("Güncellendi", self.updated_label)
        detail_box.setLayout(detail_layout)
        main_layout.addWidget(detail_box)

        self.setCentralWidget(central)

    def load_entries(self) -> None:
        if not self.vault:
            return
        entries = self.vault.list_entries()
        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            service_item = QTableWidgetItem(entry.service)
            service_item.setData(Qt.UserRole, entry.entry_id)
            self.table.setItem(row, 0, service_item)
            self.table.setItem(row, 1, QTableWidgetItem(entry.username))
            self.table.setItem(row, 2, QTableWidgetItem(", ".join(entry.tags) if entry.tags else "-"))
            self.table.setItem(row, 3, QTableWidgetItem(entry.updated_at))
        self.table.sortItems(0)
        self.table.clearSelection()
        self.display_entry(None)
        self.statusBar().showMessage(f"{len(entries)} kayıt listelendi.", 5000)

    def add_entry(self) -> None:
        dialog = EntryDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        data = dialog.get_data()
        if not data or not self.vault or not self.secure_vault or not self.master_password:
            return
        entry = VaultEntry(**data)
        self.vault.add_entry(entry)
        self.secure_vault.save_vault(self.master_password, self.vault)
        self.load_entries()
        QMessageBox.information(self, "Kayıt Eklendi", f"{entry.service} / {entry.username}")

    def delete_entry(self) -> None:
        entry = self.selected_entry()
        if not entry or not self.vault or not self.secure_vault or not self.master_password:
            QMessageBox.warning(self, "Seçim Yok", "Silmek için önce bir kayıt seçin.")
            return
        confirmed = QMessageBox.question(
            self,
            "Kayıt Silinsin mi?",
            f"{entry.service} / {entry.username} kaydını kalıcı olarak silmek istediğinize emin misiniz?",
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        self.vault.delete_entry(entry.entry_id)
        self.secure_vault.save_vault(self.master_password, self.vault)
        self.load_entries()
        QMessageBox.information(self, "Silindi", "Kayıt silindi.")

    def open_generator(self) -> None:
        dialog = PasswordGeneratorDialog(self.clipboard_guard, self)
        dialog.exec()

    def relock_vault(self) -> None:
        result = request_vault(self)
        if result is None:
            return
        self.secure_vault, self.master_password, self.vault = result
        self.load_entries()
        self.statusBar().showMessage("Kasa yeniden yüklendi.", 5000)

    def display_selected_entry(self) -> None:
        entry = self.selected_entry()
        self.display_entry(entry)

    def selected_entry(self) -> Optional[VaultEntry]:
        selection = self.table.selectedItems()
        if not selection or not self.vault:
            return None
        row = selection[0].row()
        entry_id = self.table.item(row, 0).data(Qt.UserRole)
        if not entry_id:
            return None
        try:
            return self.vault.get_entry(entry_id)
        except EntryNotFound:
            return None

    def display_entry(self, entry: Optional[VaultEntry]) -> None:
        self.current_entry = entry
        self.password_visible = False
        self.reveal_button.setText("Göster")
        if not entry:
            self.service_label.setText("-")
            self.username_label.setText("-")
            self.tags_label.setText("-")
            self.created_label.setText("-")
            self.updated_label.setText("-")
            self.password_field.setText("")
            self.notes_view.setPlainText("")
            return
        self.service_label.setText(entry.service)
        self.username_label.setText(entry.username)
        self.tags_label.setText(", ".join(entry.tags) if entry.tags else "-")
        self.created_label.setText(entry.created_at)
        self.updated_label.setText(entry.updated_at)
        self.password_field.setText(entry.password)
        self.password_field.setEchoMode(QLineEdit.Password)
        self.notes_view.setPlainText(entry.notes or "")

    def toggle_password_visibility(self) -> None:
        if not self.current_entry:
            return
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_field.setEchoMode(QLineEdit.Normal)
            self.reveal_button.setText("Gizle")
        else:
            self.password_field.setEchoMode(QLineEdit.Password)
            self.reveal_button.setText("Göster")

    def copy_password(self) -> None:
        if not self.current_entry:
            QMessageBox.warning(self, "Seçim Yok", "Önce bir kayıt seçin.")
            return
        self.clipboard_guard.copy(self.current_entry.password)
        self.statusBar().showMessage("Parola panoya kopyalandı (30 sn içinde temizlenecek).", 5000)


def request_vault(parent) -> Optional[Tuple[SecureVault, str, Vault]]:
    while True:
        dialog = UnlockDialog(parent)
        if dialog.exec() != QDialog.Accepted:
            return None
        result = dialog.get_result()
        if not result:
            return None
        storage = VaultStorage(result.vault_path)
        secure_vault = SecureVault(storage)
        try:
            if result.create_new:
                vault = secure_vault.init_vault(result.master_password)
            else:
                vault = secure_vault.load_vault(result.master_password)
            return secure_vault, result.master_password, vault
        except VaultError as exc:
            QMessageBox.critical(parent, "Kasa Hatası", str(exc))


def launch(argv: Optional[Sequence[str]] = None) -> None:
    qt_args = list(argv) if argv is not None else sys.argv
    app = QApplication(qt_args)
    app.setApplicationName("Pass Manager GUI")
    window = MainWindow(app)
    if not window.initialized:
        return
    window.show()
    app.exec()

