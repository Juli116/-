import sqlite3, traceback

def db_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            show_error("Ошибка базы данных", f"{e}\nПроверьте БД и повторите действие.")
            return None
        except Exception as e:
            with open('logs/error.log', 'a', encoding='utf-8') as f:
                f.write(traceback.format_exc() + '\n')
            show_error("Ошибка", f"{e}\nПодробности в logs/error.log")
            return None
    return wrapper

def show_error(title, text): print(f"[{title}] {text}")
def info(title, text):       print(f"[{title}] {text}")
