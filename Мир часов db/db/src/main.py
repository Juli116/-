import sys
import PySide6.QtWidgets
import PySide6.QtGui
import login as login_
from catalog import CatalogWindow

class MainWindow(PySide6.QtWidgets.QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Мир часов")
        self.setWindowIcon(PySide6.QtGui.QIcon("resources/Мир часов.ico"))
        self.setCentralWidget(CatalogWindow(user))

if __name__ == '__main__':
    app = PySide6.QtWidgets.QApplication(sys.argv)
    login = login_.LoginDialog()
    if not login.exec():
        sys.exit(0)
    win = MainWindow(login.user)
    win.showMaximized()
    sys.exit(app.exec())
