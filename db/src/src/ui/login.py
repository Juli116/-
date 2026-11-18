from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import sqlite3
import logic.error_handler

class LoginDialog(QDialog):
    def __init__(self, db_path='db/watch_store.db'):
        super().__init__()
        self.db_path = db_path
        self.user = None
        self.setWindowTitle("Мир часов — Вход")
        lay = QVBoxLayout(self)
        logo = QLabel()
        logo.setPixmap(QPixmap("resources/Мир часов.png").scaled(200, 200, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)
        self.login = QLineEdit(placeholderText="Логин")
        self.password = QLineEdit(placeholderText="Пароль")
        self.password.setEchoMode(QLineEdit.Password)
        btn = QPushButton("Войти"); btn.setObjectName("Accent"); btn.clicked.connect(self.auth)
        for w in (logo, self.login, self.password, btn):
            lay.addWidget(w)

    @logic.error_handler.db_errors
    def auth(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT user_id, role, full_name FROM users WHERE login=?",
                    (self.login.text().strip(),))
        row = cur.fetchone()
        conn.close()
        if row is None:
            QMessageBox.warning(self, "Ошибка",
                "Пользователь не найден.\nПроверьте логин и повторите вход.")
            return
        self.user = {'id': row[0], 'role': row[1], 'name': row[2]}
        self.accept()
