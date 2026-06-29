import tkinter as tk
from tkinter import ttk, messagebox
from database import SessionLocal, Inventory, get_logs_for_asset_raw, get_equipment_with_log_counts_raw, delete_equipment_by_id, MaintenanceHistory
from datetime import datetime

class MaintenanceLogTracker:
    def __init__(self, master) -> None:
        """initiating app instances"""

        # window configurations
        self.master = master
        self.master.title('MAINTENANCE LOG TRACKER')
        self.master.geometry('950x650')
        self.master.resizable(True, True)
        self.master.minsize(900, 600)

        # Main Layout Container
        main_container = ttk.Frame(self.master)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.configure("HeaderBar.TFrame", background="#2b5c8f")

        style.configure(
            "HeaderTitle.TLabel",
            background="#2b5c8f", 
            foreground='white', 
            font=("Arial", 16, "bold"))

        # Header
        header_frame = ttk.Frame(main_container, height=60, style="HeaderBar.TFrame")
        header_frame.pack(side='top', fill='x')
        header_frame.pack_propagate(False)

        header_label = ttk.Label(
            header_frame,
            text='Medical Maintenance Log Tracker',
            style="HeaderTitle.TLabel"
        )
        header_label.pack(pady=15)
        
        # Content Frame
        content_frame = ttk.Frame(main_container)
        content_frame.pack(side='top', fill='both', expand=True, pady=(10,0))

        # Splitting the content frame
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        PANEL_BG = '#f9f9f9'

        style.configure("Card.TLabelframe",
                        font=("Arial", 14, "bold"),
                        background=PANEL_BG)

        style.configure("Card.TLabelframe.Label",
                        background=PANEL_BG,
                        foreground="#2b5c8f",
                        font=("Arial", 11, "bold")
                        )
        
        #========================================================================================================
        # left sub content frame (Equipment Management)
        self.left_content_frame = ttk.LabelFrame(content_frame, text="Equipment Management", style="Card.TLabelframe")
        self.left_content_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5))

        # left sub content frame elements
        form_frame = ttk.Frame(self.left_content_frame)
        form_frame.pack(fill="x", side="top", padx=5, pady=5)

        # Equipment Name Field
        eq_name_label = ttk.Label(form_frame, text="Equipment Name:")
        eq_name_label.pack(anchor="w", padx=15, pady=(15, 2))
        
        self.eq_name_entry = ttk.Entry(form_frame)
        self.eq_name_entry.pack(fill="x", padx=15, pady=(0, 10))

        # Equipment ID / Serial No
        eq_id_label = ttk.Label(form_frame, text="Equipment ID / Serial No:")
        eq_id_label.pack(anchor="w", padx=15, pady=(5, 2))
        
        self.eq_id_entry = ttk.Entry(form_frame)
        self.eq_id_entry.pack(fill="x", padx=15, pady=(0, 10))

        # Department Field
        dept_label = ttk.Label(form_frame, text="Department / Ward:")
        dept_label.pack(anchor="w", padx=15, pady=(5, 2))
        
        self.dept_entry = ttk.Entry(form_frame)
        self.dept_entry.pack(fill="x", padx=15, pady=(0, 10))

        # Make
        issue_label = ttk.Label(form_frame, text="Make:")
        issue_label.pack(anchor="w", padx=15, pady=(5, 2))
        
        self.issue_entry = ttk.Entry(form_frame)
        self.issue_entry.pack(fill="x", padx=15, pady=(0, 20))

        # Submit Button
        style.configure(
            "HeaderTitle.TButton",
            background="#2b5c8f", 
            foreground='black', 
            font=("Arial", 12, "bold")
        )
        
        self.submit_btn = ttk.Button(
            self.left_content_frame, 
            text="Add Device To Inventory", 
            style='HeaderTitle.TButton',
            command=self.add_device_to_db 
        )
        self.submit_btn.pack(fill="x", padx=15, pady=5)

        table_container = ttk.Frame(self.left_content_frame)
        table_container.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ['id', 'name', 'make', 'dept']

        self.inventory_table = ttk.Treeview(table_container, columns=columns, show='headings')

        scrollbar = ttk.Scrollbar(table_container, orient='vertical', command=self.inventory_table.yview)
        self.inventory_table.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.inventory_table.pack(side='left', fill='both', expand=True)

        self.inventory_table.heading('id', text='Asset ID')
        self.inventory_table.heading('name', text='Equipment Name')
        self.inventory_table.heading('make', text='Make')
        self.inventory_table.heading('dept', text='Department')

        self.inventory_table.column('id', width=60, anchor='center')
        self.inventory_table.column('name', width=120, anchor='w')
        self.inventory_table.column('make', width=90, anchor='w')
        self.inventory_table.column('dept', width=100, anchor='w')

        # Synchronize interface view with live database records on boot
        self.refresh_inventory_table()

        #==========================================================================================================================================
        # right sub content frame (Maintenance History)
        self.right_content_frame = ttk.LabelFrame(content_frame, text="Maintenance History", style="Card.TLabelframe")
        self.right_content_frame.grid(row=0, column=1, sticky="nsew", padx=(0,5))

        # Create a container inside right panel
        history_container = ttk.Frame(self.right_content_frame)
        history_container.pack(fill="both", expand=True, padx=10, pady=10)

        # History Table Columns
        hist_cols = ("date", "tech", "action", "status")
        self.history_table = ttk.Treeview(history_container, columns=hist_cols, show="headings", height=10)
        
        # Add Scrollbar
        hist_scroll = ttk.Scrollbar(history_container, orient="vertical", command=self.history_table.yview)
        self.history_table.configure(yscrollcommand=hist_scroll.set)
        
        hist_scroll.pack(side="right", fill="y")
        self.history_table.pack(side="top", fill="both", expand=True)

        # Configure headings
        self.history_table.heading("date", text="Date")
        self.history_table.heading("tech", text="Technician")
        self.history_table.heading("action", text="Action Taken")
        self.history_table.heading("status", text="Device Status")

        self.history_table.column('date', width=90, anchor='center')
        self.history_table.column('tech', width=100, anchor='w')
        self.history_table.column('action', width=180, anchor='w')
        self.history_table.column('status', width=90, anchor='center')

        self.status_msg_label = ttk.Label(
            self.right_content_frame, 
            text="Double-click an asset on the left to view history logs.", 
            font=("Arial", 10, "italic"),
            foreground="gray"
        )
        self.status_msg_label.pack(pady=10)

        # Action Button (Initially disabled until a device is selected)
        self.add_log_btn = ttk.Button(
            self.right_content_frame, 
            text="＋ Log New Maintenance Action", 
            state="disabled",
            command=self.open_maintenance_popup
        )
        self.add_log_btn.pack(fill="x", padx=15, pady=(0, 15))
        
        # Bind double-click action to the inventory table handler
        self.inventory_table.bind("<Double-1>", self.on_asset_double_click)

        # Activate the right-click popup context menu binding
        self.setup_context_menu()

    # =====================================================================
    # DATABASE CONNECTIVITY METHODS
    # =====================================================================

    def refresh_inventory_table(self):
        """Clears and re-populates the inventory table from the live database."""
        for row in self.inventory_table.get_children():
            self.inventory_table.delete(row)
            
        records = get_equipment_with_log_counts_raw()
        for row in records:
            self.inventory_table.insert("", "end", values=(row[0], row[1], row[2], row[3]))

    def add_device_to_db(self):
        """Pulls input data fields from entry boxes and commits them to the database."""
        name = self.eq_name_entry.get().strip()
        serial = self.eq_id_entry.get().strip()
        dept = self.dept_entry.get().strip()
        make = self.issue_entry.get().strip()

        if not (name and serial and dept and make):
            self.status_msg_label.config(text="⚠️ Error: All fields are required to add a device.", foreground="#d9534f")
            return

        with SessionLocal() as db:
            try:
                new_device = Inventory(name=name, serial_no=serial, dept=dept, make=make)
                db.add(new_device)
                db.commit()
                
                self.eq_name_entry.delete(0, tk.END)
                self.eq_id_entry.delete(0, tk.END)
                self.dept_entry.delete(0, tk.END)
                self.issue_entry.delete(0, tk.END)
                
                self.refresh_inventory_table()
                self.status_msg_label.config(text=f"✅ Asset '{name}' added successfully!", font=("Arial", 10, "normal"), foreground="green")
            except Exception:
                db.rollback()
                self.status_msg_label.config(text="⚠️ Error: Serial Number already exists.", foreground="#d9534f")

    def on_asset_double_click(self, event):
        """Triggered when a user double-clicks an item in the main inventory table."""
        for row in self.history_table.get_children():
            self.history_table.delete(row)
            
        selected_item = self.inventory_table.selection()
        if not selected_item:
            return
            
        item_data = self.inventory_table.item(selected_item[0])['values']
        self.selected_asset_id = int(item_data[0]) 
        asset_name = item_data[1]

        real_logs = get_logs_for_asset_raw(self.selected_asset_id)

        if real_logs:
            for log in real_logs:
                self.history_table.insert("", "end", values=(log[0], log[1], log[2], log[3]))
                
            self.status_msg_label.config(text=f"Showing logs for: {asset_name}", font=("Arial", 9, "normal"), foreground="black")
        else:
            self.status_msg_label.config(
                text=f"ℹ No maintenance history records found for {asset_name}.", 
                font=("Arial", 10, "italic"),
                foreground="#d9534f" 
            )
            
        self.add_log_btn.config(state="normal")

    def open_maintenance_popup(self):
        """Opens a secure popup modal to enter new technical maintenance details."""
        popup = tk.Toplevel(self.master)
        popup.title("Log New Maintenance Event")
        popup.geometry("350x400")
        popup.transient(self.master) 
        popup.grab_set()             

        ttk.Label(popup, text="Technician Name:").pack(anchor="w", padx=20, pady=(20, 2))
        tech_entry = ttk.Entry(popup)
        tech_entry.pack(fill="x", padx=20)

        ttk.Label(popup, text="Action Details / Parts Replaced:").pack(anchor="w", padx=20, pady=(15, 2))
        details_entry = ttk.Entry(popup) 
        details_entry.pack(fill="x", padx=20)

        ttk.Label(popup, text="Device Status Post-Service:").pack(anchor="w", padx=20, pady=(15, 2))
        status_combobox = ttk.Combobox(popup, values=["Operational", "Under Repair", "Decommissioned"], state="readonly")
        status_combobox.pack(fill="x", padx=20)
        status_combobox.set("Operational")

        def save_and_close():
            
            tech = tech_entry.get().strip()
            details = details_entry.get().strip()
            status = status_combobox.get()
            current_date = datetime.now().strftime("%Y-%m-%d") 

            if not (tech and details):
                return 

            with SessionLocal() as db:
                new_log = MaintenanceHistory(
                    equipment_id=self.selected_asset_id,
                    date_run=current_date,
                    technician=tech,
                    action_taken=details,
                    status=status
                )
                db.add(new_log)
                db.commit()
            
            popup.destroy()
            self.refresh_history_after_insert()

        ttk.Button(popup, text="💾 Save Log Entry", command=save_and_close).pack(fill="x", padx=20, pady=30)

    def refresh_history_after_insert(self):
        """Refreshes the history panel display after a new log is successfully committed."""
        for row in self.history_table.get_children():
            self.history_table.delete(row)
            
        real_logs = get_logs_for_asset_raw(self.selected_asset_id)
        if real_logs:
            for log in real_logs:
                self.history_table.insert("", "end", values=(log[0], log[1], log[2], log[3]))

    # =====================================================================
    # CONTEXT RIGHT-CLICK DELETE LOGIC
    # =====================================================================

    def setup_context_menu(self):
        """Creates a right-click pop-up menu for deleting assets."""
        self.context_menu = tk.Menu(self.master, tearoff=0)
        self.context_menu.add_command(label="❌ Delete Device from Inventory", command=self.delete_selected_asset)
        
        # Windows & Linux Right-Click binding
        self.inventory_table.bind("<Button-3>", self.show_context_menu)
        # macOS Secondary Trackpad click binding
        self.inventory_table.bind("<Button-2>", self.show_context_menu)

    def show_context_menu(self, event):
        """Displays the right-click menu exactly where the cursor is."""
        row_id = self.inventory_table.identify_row(event.y)
        if row_id:
            self.inventory_table.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)

    def delete_selected_asset(self):
        """Extracts the active row selection and drops it from the database."""
        selected_item = self.inventory_table.selection()
        if not selected_item:
            return
            
        item_data = self.inventory_table.item(selected_item[0])['values']
        asset_id = int(item_data[0])
        asset_name = item_data[1]
        
        # Security/Confirmation check before executing irreversible truncation operations
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete '{asset_name}'?\nThis will clear all its maintenance history logs too!"):
            delete_equipment_by_id(asset_id)
            
            # Instantly clear the history panel right-side view if the active focus item was just dropped
            if hasattr(self, 'selected_asset_id') and self.selected_asset_id == asset_id:
                for row in self.history_table.get_children():
                    self.history_table.delete(row)
                self.status_msg_label.config(text="Double-click an asset on the left to view history logs.", foreground="gray")
                self.add_log_btn.config(state="disabled")
                
            # Sync treeview
            self.refresh_inventory_table()
            self.status_msg_label.config(text=f"🗑️ Asset '{asset_name}' has been deleted.", foreground="#d9534f")