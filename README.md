# Medical Maintenance Log Tracker

A professional desktop application designed for clinical asset management and equipment maintenance lifecycles. Built using Python, the application features an asynchronous-feel GUI dashboard, a structurally robust object-relational mapping (ORM) backend, and high-speed cascading data purges.

## Key Features

* **Equipment Inventory Management:** Effortlessly add, track, and manage clinical assets with validation ensuring unique serial number registration.
* **Granular Maintenance Logging:** Double-click any asset to pull its complete historical log registry, add fresh technical actions, parts replaced, and post-service device statuses.
* **High-Speed Deletion Cascades:** Decommission non-functional or retired units seamlessly with a right-click context menu. SQLite triggers automated cascades to drop all underlying history logs instantly ($O(1)$ item execution mapping).
* **Robust Multi-File Architecture:** Clean separation of concerns between data persistence schemas, business logic, and UI execution states.

---

## Technical Stack

* **Frontend:** Python `tkinter` + `ttk` (Hierarchical themed grid layout constraints).
* **Database Layer:** `SQLite` (High-performance file-based storage).
* **ORM Backend:** `SQLAlchemy 2.0` (Type-annotated declarative base models).

---

## File Structure & Topology

The codebase is organized into three distinct structural modules:
    ```text
    ├── database.py       # Core ORM schemas, database initialization, and raw SQL queries
    ├── ui.py             # Main GUI panels, multi-frame context forms, and event handling
    └── main.py           # Application entry point (triggers database migrations and UI mainloop)

---

## Getting Started

### Prerequisites
* Python 3.8 or higher installed on your system.
* SQLAlchemy installed in your environment.

### Installation
1. Clone the repository to your local machine:
   ```bash
   cd medical-maintenance-log-tracker

2. Navigate into the project directory:
   ```bash
   git clone (https://github.com/yourusername/medical-maintenance-log-tracker.git)


### Running the Application
* Launch the script directly from your terminal:
    ```bash
    python main.py


## With uv

Install uv (if you do not have it):

* On macOS/Linux
    ```bash
    curl -LsSf https://astral.sh | sh

* On Windows
    ```bash
    powershell -c "irm https://astral.sh | iex"

* Run the project instantly:
    ```bash
    uv run main.py


### License
    This project is open-source and available under the MIT License.