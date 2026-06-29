import tkinter as tk
from ui import MaintenanceLogTracker
from database import initialize_database


def main():
    """Instantiating the ui window and initializing core services."""

    # 1. Build or verify the physical SQLite schema on startup
    initialize_database()

    # 2. Spin up the Tkinter application environment
    root = tk.Tk()
    app = MaintenanceLogTracker(root)
    root.mainloop()

if __name__ == '__main__':
    main()