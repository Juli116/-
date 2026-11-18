STYLE = """
QWidget { font-family: 'Calibri'; font-size: 14px; color: #000000; background: #FFFFFF; }
QMainWindow, #Sidebar { background: #D2F6E7; }
QLabel#Header { font-size: 20px; font-weight: bold; background: transparent; }
QPushButton { background: #D2F6E7; border: 1px solid #70B2AF; border-radius: 4px; padding: 6px 14px; }
QPushButton:hover { background: #70B2AF; color: #FFFFFF; }
QPushButton#Accent { background: #70B2AF; color: #000000; font-weight: bold; }
QLineEdit, QComboBox, QSpinBox, QTableWidget {
    background: #FFFFFF; border: 1px solid #70B2AF; border-radius: 4px; padding: 4px; }
QFrame#Card { background: #FFFFFF; border: 1px solid #70B2AF; border-radius: 6px; }
QFrame#CardLow { background: #ff8080; border: 1px solid #70B2AF; border-radius: 6px; }
"""

def fmt_price(p):  return f"{p:,.2f}".replace(',', ' ') + " ₽"
def fmt_date(iso): return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}"     # ДД.ММ.ГГГГ
