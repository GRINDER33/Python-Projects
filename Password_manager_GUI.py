# Password manager GUI

import sys
import os 
import random
from cryptography.fernet import Fernet
import string
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTextEdit, QMessageBox, QSpinBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QInputDialog, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt

# Configuration

FILE_PATH = "Password_Manager.txt"        # change if you want another path
KEY_PATH = "secret.key"
BACKUP_PATH = "Password_Manager_backup.txt"
MASTER_PASSWORD = "admin123"                # change to something secure for real use

# characters used for password generation

PASS_LIB = list(string.punctuation + string.digits + string.ascii_letters)

# Key management

# Encryption key management

def load_key():
    """Creates or loads encryption key."""
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_PATH, "rb") as key_file:
            key = key_file.read()
    return Fernet(key)

f = load_key()

# --Logic and Generation--

# Password Generation
def generate_password(length: int) -> str:
    return "".join(random.choice(PASS_LIB) for _ in range(length))

# Strength of Password
def check_strength(password):
    length = len(password)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    score = sum([has_lower, has_upper, has_digit, has_symbol])

    # Determine strength
    if length < 6 or score <= 1:
        return "Weak 🔴"
    elif 6 <= length < 10 and score >= 2:
        return "Medium 🟡"
    elif length >= 10 and score >= 3:
        return "Strong 🟢"
    else:
        return "Very Strong 🟣"

# Saving the entry to both actual data file with password encrypted and to backup file non encrypted 
def save_entry(username: str, email: str, plain_password: str):
    # Encrypting the password
    enc = f.encrypt(plain_password.encode()).decode()
    
    # Making sure the directory exists
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok = True) if os.path.dirname(FILE_PATH) else None

    # Writing to file
    with open(FILE_PATH, "a", encoding = "UTF-8") as file:
        file.write("\n---------------------------\n")
        file.write(f"Username: {username}\n")
        file.write(f"Email: {email}\n")
        file.write(f"Password: {enc}\n")

    # Writing to backup file
    with open(BACKUP_PATH, "a", encoding = "UTF-8") as bfile:
        bfile.write("\n---------------------------\n")
        bfile.write(f"Username: {username}\n")
        bfile.write(f"Email: {email}\n")
        bfile.write(f"Password: {plain_password}\n")

def parsing_file_base():
    # Return the file as readable/organisable key:value pair

    # entries will be the dictionary of key value pairs containing username, email, password as blocks
    entries = []
    if not os.path.exists(FILE_PATH):
        return entries
    
    # Read the main file encode using utf-8 and remove all the spaces and add in raw_text
    raw_text = open(FILE_PATH, "r", encoding = "utf-8").read().strip()

    if not raw_text:
        return entries
    
    # Splits the data using "---------------------------\n" wherever found in the data file
    blocks = raw_text.split("---------------------------\n")

    for block in blocks:
        # Remove spaces in blocks
        block = block.strip()
        # if block is empty continue
        if not block:
            continue
        
        # lines in a block 
        lines = block.splitlines()
        entry = {}

        # Iterate over each line in the iterated block
        for line in lines:
            if line.startswith("Username"):
                entry["Username"] = line.replace("Username: ", "").strip()

            elif line.startswith("Email: "):
                entry["Email"] = line.replace("Email: ", "").strip()

            elif line.startswith("Password"):
                enc = line.replace("Password: ", "").strip()
                try:
                    
                    #Try decryting the password and add it as value
                    decrypted = f.decrypt(enc.encode()).decode()
                    entry["Password"] = decrypted

                except Exception:
                    # if decrypt fails, keep the encrypted string with marker
                    entry["Password"] = enc + " (decryption failed)"
        # If entry has data append it to entries
        if entry:
            entries.append(entry)

    return entries

# GUI Window

def ask_master_password(parent=None):
    """Popup input dialog for master password (returns string or None)."""
    text, ok = QInputDialog.getText(parent, "Master Password", "Enter master password:", QLineEdit.Password)
    if ok:
        return text.strip()
    return None

# To confirn savinf the password
class SaveConfirmDialog(QDialog):       
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Save")
        self.result = False
        input_row = QFormLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        input_row.addRow("Enter master password to confirm:", self.password_input)
        box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        input_row.addWidget(box)

        self.setLayout(input_row)

    def accept(self):
        if self.password_input.text().strip() == MASTER_PASSWORD:
            self.result = True
            super().accept()
        else:
            QMessageBox.warning(self, "Wrong password", "Master password incorrect.")
            self.result = False
    
# Main window GUI

class PasswordManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Manager")
        self.setFixedSize(820, 640)
        self.init_UI()
    
    def init_UI(self):
        main_layout = QVBoxLayout()
        header = QLabel("<h2 style= 'margin: 6px'>🔒 Password Manager</h2>")
        main_layout.addWidget(header)
        self.setStyleSheet("QPushButton { padding: 6px; } QLineEdit { padding: 4px }")

        # Top Row Generator

        generator_layout = QHBoxLayout()
        generator_layout.addWidget(QLabel("Length:"))
        self.len_input = QSpinBox()
        self.len_input.setRange(4, 64)
        self.len_input.setValue(12)
        generator_layout.addWidget(self.len_input)
        self.generator_button = QPushButton("Generate Password")
        self.generator_button.clicked.connect(self.on_generate)              
        generator_layout.addWidget(self.generator_button)
        self.generator_output = QLineEdit()
        self.generator_output.setReadOnly(True)
        generator_layout.addWidget(self.generator_output)
        self.strength_label = QLabel("")
        generator_layout.addWidget(self.strength_label)
        main_layout.addLayout(generator_layout)

        # Middle Row Add/Save Manual

        add_layout = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("<b> Add/Save Password </b>"))
        form_layout = QVBoxLayout()
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Enter Username")
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Enter Email")
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Password (Leave Blank to Generate)")
        self.add_gen_button = QPushButton("Fill Generated")
        self.add_gen_button.clicked.connect(self.fill_generated_empty)             
        form_layout.addWidget(self.input_username)
        form_layout.addWidget(self.input_email)
        form_layout.addWidget(self.input_password)
        form_layout.addWidget(self.add_gen_button)
        left.addLayout(form_layout)
        add_layout.addLayout(left)

        # Middle Right Layout

        right = QVBoxLayout()
        self.save_button = QPushButton("Save Entry (requires master password)")
        self.save_button.clicked.connect(self.on_save_entry)                
        self.manual_add_button = QPushButton("Manual Add (No confirm)")
        self.manual_add_button.clicked.connect(self.on_manual_add)
        right.addWidget(self.save_button)
        right.addWidget(self.manual_add_button)
        add_layout.addLayout(right)

        # Add middle to the main layout

        main_layout.addLayout(add_layout)

        # Search/Sort Row

        search_sort_layout = QHBoxLayout()
        self.search_choice = QComboBox()
        self.search_choice.addItems(["Search by Username", "Search by Email"])
        search_sort_layout.addWidget(self.search_choice)
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter Search Keyword")
        search_sort_layout.addWidget(self.keyword_input)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_search)             
        search_sort_layout.addWidget(self.search_button)
        self.show_all_button = QPushButton("Show All")
        self.show_all_button.clicked.connect(self.refresh_table)            
        search_sort_layout.addWidget(self.show_all_button)
        
        search_sort_layout.addStretch()
        self.sort_label = QLabel("Sort:")
        search_sort_layout.addWidget(self.sort_label)
        self.sort_choice = QComboBox()
        self.sort_choice.addItems(["No Sort","By Username", "By Email"])
        search_sort_layout.addWidget(self.sort_choice)
        self.apply_sort_button = QPushButton("Apply Sort")
        self.apply_sort_button.clicked.connect(self.on_sort)            
        search_sort_layout.addWidget(self.apply_sort_button)

        # Add search sort layout to main layout

        main_layout.addLayout(search_sort_layout)

        # Data table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Username", "Email", "Password"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(self.table.SelectRows)
        main_layout.addWidget(self.table)

        # Bottom Row
        bottom = QHBoxLayout()
        self.unlock_view_button = QPushButton("Show (Unlock View)")
        self.unlock_view_button.clicked.connect(self.on_show_unlocked)           
        bottom.addWidget(self.unlock_view_button)
        self.backup_export_button = QPushButton("Export Backup (plain)")
        self.backup_export_button.clicked.connect(self.on_export_backup)            
        bottom.addWidget(self.backup_export_button)
        self.clear_view_button = QPushButton("Clear Table View")
        self.clear_view_button.clicked.connect(lambda: self.table.setRowCount(0))
        bottom.addWidget(self.clear_view_button)
        bottom.addStretch()

        # Add bottom row to the main layout

        main_layout.addLayout(bottom)

        # Set layout to show on main window
        self.setLayout(main_layout)

# ---- GUI funtions ----

    def on_generate(self):
        # Gets the length of the password to be generated
        length = self.len_input.value()
        password = generate_password(length)
        self.generator_output.setText(password)
        self.strength_label.setText(check_strength(password))

    def fill_generated_empty(self):
        if not self.generator_output.text():
            self.on_generate()
        # Sets generated password in password box if clicked on fill generated
        self.input_password.setText(self.generator_output.text())

    def on_save_entry(self):
        # Ask master password in dialog box
        dialog = SaveConfirmDialog(self)
        if dialog.exec_() and dialog.result:
            username = self.input_username.text().strip()
            email = self.input_email.text().strip()
            password = self.input_password.text().strip()
            
            if not password:
                # Generate one 
                password = generate_password(self.len_input.value())
            if not username:
                QMessageBox.warning(self, "Missing", "Please enter a Username/Site Name")
                return
            
            # Save
            try:
                save_entry(username, email, password)
                QMessageBox.information(self, "Saved", f"Entry Saved for username: {username}")
                self.refresh_table()

                # clear fields
                self.input_username.clear(); self.input_email.clear(); self.input_password.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {e}")
        
    def on_manual_add(self):
        # manual add without confirming master password (keeps encryption)
        username = self.input_username.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()

        if not password:
            QMessageBox.warning(self, "Missing", "Please enter a password or generate one.")
            return
        if not username:
            QMessageBox.warning(self, "Missing", "Please enter a Username/Site Name.")
            return
            # Save
        try:

            save_entry(username, email, password)
            QMessageBox.information(self, "Saved", f"Entry Saved for username: {username}")
            self.refresh_table()

            # clear fields
            self.input_username.clear(); self.input_email.clear(); self.input_password.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")

    def on_show_unlocked(self):
        # Ask for master password then show the decrypted entries
        text = ask_master_password(self)

        if text is None:
            return
        if text != MASTER_PASSWORD:
            QMessageBox.warning(self, "Denied", "Master password incorrect.")
            return
        self.refresh_table(show_passwords=True)

    def on_sort(self):
        choice = self.sort_choice.currentText()
        entries = parsing_file_base()
        
        # Sort by username
        if choice == "By Username":
            entries.sort(key = lambda x: x.get("Username", "").lower())

        # Sort by email
        elif choice == "By Email":
            entries.sort(key = lambda x: x.get("Email", "").lower())

        self.entries_cache = entries
        self.populate_table(entries, show_passwords = True)   

    def on_search(self):
        term = self.keyword_input.text().strip().lower()
        if not term:
            QMessageBox.information(self, "Search", "Enter keyword to search.")
            return
        by = self.search_choice.currentIndex()   # 0 username, 1 email
        entries = parsing_file_base()
        found = []

        for entry in entries:
            if by == 0 and term in entry.get("Username", "").lower():
                found.append(entry)
            elif by == 1 and term in entry.get("Email", "").lower():
                found.append(entry)
        if not found:
            QMessageBox.information(self, "Search", "No matching entries found.")
            return
        self.entries_cache = found
        self.populate_table(found, show_passwords = True)

    def on_export_backup(self):
        # writes current parsed entries to BACKUP_PATH as plain — warn user
        reply = QMessageBox.question(
            self, "Export plain backup",
            f"This will write decrypted passwords in plain to:\n{BACKUP_PATH}\n\nAre you sure?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return
        
        # require master password

        text = ask_master_password(self)
        
        if text != MASTER_PASSWORD:
            QMessageBox.warning(self, "Denied", "Master password incorrect.")
            return
        entries = parsing_file_base()

        try:
            with open(BACKUP_PATH, "w") as bfile:
                    for entry in entries:
                        bfile.write("---------------------------\n")
                        bfile.write(f"Username: {entry.get('Username','')}\n")
                        bfile.write(f"Email: {entry.get('Email','')}\n")
                        bfile.write(f"Password: {entry.get('Password','')}\n")

                    QMessageBox.information(self, "Exported", f"Backup written to:\n{BACKUP_PATH}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

    def refresh_table(self, show_passwords: bool = False):
        """Reload (encrypted) entries. If show_passwords True, attempt to decrypt and display."""
        entries = parsing_file_base()
        self.entries_cache = entries
        # default: hide passwords until user unlocks
        self.populate_table(entries, show_passwords)

    def populate_table(self, entries, show_passwords: bool):
        self.table.setRowCount(0)
        for entry in entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(entry.get("Username", "") or ""))
            self.table.setItem(row, 1, QTableWidgetItem(entry.get("Email", "") or ""))
            password = entry.get("Password", "")
            if not show_passwords:
                # Hide actual passwords
                if " (decryption failed)" in password:
                    display_pw = "(encrypted / failed)"
                elif password:
                    display_pw = "••••••••"
                else:
                    display_pw = ""
            else:
                display_pw = password
            self.table.setItem(row, 2, QTableWidgetItem(display_pw))




# ---------- run ----------
def main():

    print(os.getcwd())
    app = QApplication(sys.argv)
    window = PasswordManagerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

    