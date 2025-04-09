import tkinter as tk
import database
import login
from gui import MisaApp

database.create_files()
database.init_user_file()

def run_app(role):
    root = tk.Tk()
    app = MisaApp(root, role)  # Truyền quyền (role) vào ứng dụng
    root.mainloop()

if __name__ == "__main__":
    login.show_login_window(run_app)
