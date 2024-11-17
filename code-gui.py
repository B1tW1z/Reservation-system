import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector as sql
from random import randint
from datetime import datetime
import re

class IRCTCApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IRCTC Ticket Reservation System")
        self.root.geometry("800x600")
        
        # Database connection
        self.current_user = None
        self.conn = None
        self.cursor = None
        
        # Start with login frame
        self.show_db_connection_frame()
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
        
    def show_db_connection_frame(self):
        self.clear_window()
        
        frame = ttk.LabelFrame(self.root, text="Database Connection", padding="20")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ttk.Label(frame, text="Hostname:").grid(row=0, column=0, pady=5, sticky="w")
        ttk.Label(frame, text="Username:").grid(row=1, column=0, pady=5, sticky="w")
        ttk.Label(frame, text="Password:").grid(row=2, column=0, pady=5, sticky="w")
        
        hostname_entry = ttk.Entry(frame)
        username_entry = ttk.Entry(frame)
        password_entry = ttk.Entry(frame, show="*")
        
        hostname_entry.grid(row=0, column=1, pady=5, padx=5)
        username_entry.grid(row=1, column=1, pady=5, padx=5)
        password_entry.grid(row=2, column=1, pady=5, padx=5)
        
        def connect_db():
            try:
                self.conn = sql.connect(
                    host=hostname_entry.get(),
                    user=username_entry.get(),
                    password=password_entry.get()
                )
                self.conn.autocommit = True
                self.cursor = self.conn.cursor()
                
                # Create database and tables if they don't exist
                self.setup_database()
                self.show_login_frame()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to connect to database: {str(e)}")
        
        ttk.Button(frame, text="Connect", command=connect_db).grid(row=3, column=0, columnspan=2, pady=20)
        
    def setup_database(self):
        try:
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS IRCTC")
            self.cursor.execute("USE IRCTC")
            
            # Create accounts table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INT PRIMARY KEY,
                    pass VARCHAR(16),
                    name VARCHAR(100),
                    sex CHAR(1),
                    age VARCHAR(3),
                    dob DATE,
                    ph_no CHAR(10)
                )
            """)
            
            # Create tickets table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INT,
                    PNR INT,
                    train VARCHAR(25),
                    doj DATE,
                    tfr VARCHAR(100),
                    tto VARCHAR(100)
                )
            """)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup database: {str(e)}")
    
    def show_login_frame(self):
        self.clear_window()
        
        frame = ttk.LabelFrame(self.root, text="Login", padding="20")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ttk.Label(frame, text="Welcome to IRCTC Ticket Reservation Portal", font=("Arial", 14, "bold")).pack(pady=20)
        
        def show_create_account():
            self.show_create_account_frame()
            
        def show_login():
            self.show_login_details_frame()
            
        ttk.Button(frame, text="Create New Account", command=show_create_account).pack(pady=10)
        ttk.Button(frame, text="Login", command=show_login).pack(pady=10)
        ttk.Button(frame, text="Exit", command=self.root.quit).pack(pady=10)
    
    def show_create_account_frame(self):
        self.clear_window()
        
        frame = ttk.LabelFrame(self.root, text="Create Account", padding="20")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Generate random ID
        user_id = randint(1000, 10000)
        
        ttk.Label(frame, text=f"Your Generated ID: {user_id}").grid(row=0, column=0, columnspan=2, pady=10)
        
        fields = [
            ("Password:", "password"),
            ("Name:", "name"),
            ("Gender (M/F/O):", "gender"),
            ("Age:", "age"),
            ("Date of Birth (YYYY-MM-DD):", "dob"),
            ("Phone Number:", "phone")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i+1, column=0, pady=5, sticky="w")
            entry = ttk.Entry(frame)
            if key == "password":
                entry.config(show="*")
            entry.grid(row=i+1, column=1, pady=5, padx=5)
            entries[key] = entry
        
        def validate_and_create():
            # Basic validation
            if not all(entry.get() for entry in entries.values()):
                messagebox.showerror("Error", "All fields are required!")
                return
                
            try:
                # Insert into database
                self.cursor.execute("""
                    INSERT INTO accounts VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    entries['password'].get(),
                    entries['name'].get(),
                    entries['gender'].get().upper(),
                    entries['age'].get(),
                    entries['dob'].get(),
                    entries['phone'].get()
                ))
                
                messagebox.showinfo("Success", "Account created successfully!")
                self.show_login_details_frame()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create account: {str(e)}")
        
        ttk.Button(frame, text="Create Account", command=validate_and_create).grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Back", command=self.show_login_frame).grid(row=len(fields)+2, column=0, columnspan=2, pady=10)
    
    def show_login_details_frame(self):
        self.clear_window()
        
        frame = ttk.LabelFrame(self.root, text="Login", padding="20")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ttk.Label(frame, text="ID:").grid(row=0, column=0, pady=5, sticky="w")
        ttk.Label(frame, text="Password:").grid(row=1, column=0, pady=5, sticky="w")
        
        id_entry = ttk.Entry(frame)
        password_entry = ttk.Entry(frame, show="*")
        
        id_entry.grid(row=0, column=1, pady=5, padx=5)
        password_entry.grid(row=1, column=1, pady=5, padx=5)
        
        def login():
            try:
                self.cursor.execute("""
                    SELECT id, name FROM accounts 
                    WHERE id = %s AND pass = %s
                """, (id_entry.get(), password_entry.get()))
                
                result = self.cursor.fetchone()
                if result:
                    self.current_user = result
                    messagebox.showinfo("Success", f"Welcome back {result[1]}!")
                    self.show_main_menu()
                else:
                    messagebox.showerror("Error", "Invalid credentials!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Login failed: {str(e)}")
        
        ttk.Button(frame, text="Login", command=login).grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Back", command=self.show_login_frame).grid(row=3, column=0, columnspan=2, pady=10)
    
    def show_main_menu(self):
        self.clear_window()
        
        frame = ttk.LabelFrame(self.root, text="Main Menu", padding="20")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        options = [
            ("Purchase a Ticket", self.show_buy_ticket_frame),
            ("Check Ticket Status", self.show_ticket_status_frame),
            ("Request a Refund", self.show_cancel_ticket_frame),
            ("Account Settings", self.show_account_settings_frame),
            ("Logout", self.show_login_frame),
            ("Exit", self.root.quit)
        ]
        
        for i, (text, command) in enumerate(options):
            ttk.Button(frame, text=text, command=command).pack(pady=10)
    
    def show_buy_ticket_frame(self):
        self.clear_window()
        
        frame = ttk.LabelFrame(self.root, text="Purchase Ticket", padding="20")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        pnr = randint(100000, 1000000)
        ttk.Label(frame, text=f"Your PNR: {pnr}").grid(row=0, column=0, columnspan=2, pady=10)
        
        fields = [
            ("Train Name:", "train"),
            ("Date of Journey (YYYY-MM-DD):", "doj"),
            ("Departing Station:", "from"),
            ("Destination Station:", "to")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i+1, column=0, pady=5, sticky="w")
            entry = ttk.Entry(frame)
            entry.grid(row=i+1, column=1, pady=5, padx=5)
            entries[key] = entry
        
        def purchase_ticket():
            try:
                self.cursor.execute("""
                    INSERT INTO tickets VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    self.current_user[0],
                    pnr,
                    entries['train'].get(),
                    entries['doj'].get(),
                    entries['from'].get(),
                    entries['to'].get()
                ))
                
                messagebox.showinfo("Success", "Ticket purchased successfully!")
                self.show_main_menu()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to purchase ticket: {str(e)}")
        
        ttk.Button(frame, text="Purchase", command=purchase_ticket).grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Back", command=self.show_main_menu).grid(row=len(fields)+2, column=0, columnspan=2, pady=10)
    
    def show_ticket_status_frame(self):
        self.clear_window()
        
        frame = ttk.LabelFrame(self.root, text="Check Ticket Status", padding="20")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ttk.Label(frame, text="Enter PNR:").pack(pady=5)
        pnr_entry = ttk.Entry(frame)
        pnr_entry.pack(pady=5)
        
        def check_status():
            try:
                self.cursor.execute("""
                    SELECT * FROM tickets WHERE pnr = %s AND id = %s
                """, (pnr_entry.get(), self.current_user[0]))
                
                result = self.cursor.fetchone()
                if result:
                    status_text = f"""
                    Train: {result[2]}
                    Date of Journey: {result[3]}
                    From: {result[4]}
                    To: {result[5]}
                    """
                    messagebox.showinfo("Ticket Status", status_text)
                else:
                    messagebox.showerror("Error", "Ticket not found!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to check status: {str(e)}")
        
        ttk.Button(frame, text="Check Status", command=check_status).pack(pady=20)
        ttk.Button(frame, text="Back", command=self.show_main_menu).pack(pady=10)
    
    def show_cancel_ticket_frame(self):
        self.clear_window()
        
        frame = ttk.LabelFrame(self.root, text="Cancel Ticket", padding="20")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ttk.Label(frame, text="Enter PNR:").pack(pady=5)
        pnr_entry = ttk.Entry(frame)
        pnr_entry.pack(pady=5)
        
        def cancel_ticket():
            try:
                self.cursor.execute("""
                    DELETE FROM tickets 
                    WHERE pnr = %s AND id = %s
                """, (pnr_entry.get(), self.current_user[0]))
                
                if self.cursor.rowcount > 0:
                    messagebox.showinfo("Success", "Ticket cancelled successfully! You will be refunded shortly.")
                    self.show_main_menu()
                else:
                    messagebox.showerror("Error", "Ticket not found!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel ticket: {str(e)}")
        
        ttk.Button(frame, text="Cancel Ticket", command=cancel_ticket).pack(pady=20)
        ttk.Button(frame, text="Back", command=self.show_main_menu).pack(pady=10)
    
    def show_account_settings_frame(self):
        self.clear_window()
        
        frame = ttk.LabelFrame(self.root, text="Account Settings", padding="20")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
def show_account_settings_frame(self):
    self.clear_window()
    
    # Check if user is logged in
    if not self.current_user:
        messagebox.showerror("Error", "No user logged in!")
        self.show_login_frame()
        return
        
    frame = ttk.LabelFrame(self.root, text="Account Settings", padding="20")
    frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    # Get current user details
    try:
        self.cursor.execute("""
            SELECT * FROM accounts WHERE id = %s
        """, (self.current_user[0],))
        
        user_details = self.cursor.fetchone()
        if not user_details:
            messagebox.showerror("Error", "User details not found!")
            self.show_login_frame()
            return
            
        # Display basic info
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill='x', pady=10)
        
        ttk.Label(info_frame, text=f"User ID: {user_details[0]}", font=("Arial", 12)).pack(pady=5)
        ttk.Label(info_frame, text=f"Name: {user_details[2]}", font=("Arial", 12)).pack(pady=5)
        
        def show_details():
            details_text = f"""
            ID: {user_details[0]}
            Name: {user_details[2]}
            Gender: {user_details[3]}
            Age: {user_details[4]}
            Date of Birth: {user_details[5]}
            Phone Number: {user_details[6]}
            """
            messagebox.showinfo("Account Details", details_text.strip())
        
        def delete_account():
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete your account?"):
                try:
                    # Check for existing tickets
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM tickets WHERE id = %s
                    """, (self.current_user[0],))
                    
                    ticket_count = self.cursor.fetchone()[0]
                    
                    if ticket_count > 0:
                        if messagebox.askyesno("Existing Tickets", 
                                             f"You have {ticket_count} active ticket(s). Do you want to cancel them and request refunds?"):
                            self.cursor.execute("""
                                DELETE FROM tickets WHERE id = %s
                            """, (self.current_user[0],))
                            messagebox.showinfo("Success", "Tickets cancelled and refunds will be processed!")
                    
                    # Delete account
                    self.cursor.execute("""
                        DELETE FROM accounts WHERE id = %s
                    """, (self.current_user[0],))
                    
                    messagebox.showinfo("Success", "Account deleted successfully!")
                    self.current_user = None
                    self.show_login_frame()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete account: {str(e)}")
        
        # Buttons frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=20)
        
        # Create buttons
        ttk.Button(button_frame, 
                  text="Show Full Details", 
                  command=show_details).pack(pady=5, fill='x')
        
        ttk.Button(button_frame, 
                  text="Delete Account", 
                  command=delete_account).pack(pady=5, fill='x')
        
        ttk.Button(button_frame, 
                  text="Back to Main Menu", 
                  command=self.show_main_menu).pack(pady=5, fill='x')
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load account settings: {str(e)}")
        self.show_main_menu()
        
def clear_window(self):
    """Clear all widgets from the window"""
    for widget in self.root.winfo_children():
        widget.destroy()

def run(self):
    """Start the application"""
    self.root.mainloop()

if __name__ == "__main__":
    app = IRCTCApp()
    app.run()