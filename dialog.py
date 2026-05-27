#functionality for pop up windows
import re

from PyQt5.QtWidgets import (QDialog, QLineEdit, QLabel, QCheckBox, QDialogButtonBox,
                             QFormLayout, QVBoxLayout)

EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

#dialog for adding customer to db
class CreateRecord(QDialog):
    def __init__(self, parent=None):
        super().__init__()

        self.setWindowTitle("Add Customer")

        self.first_name_entry = QLineEdit(self)
        self.last_name_entry = QLineEdit(self)
        self.email_entry = QLineEdit(self)
        self.duplicate_notice = QLabel(self)
        self.duplicate_notice.setText("Entries with duplicate emails will be ignored.")
        self.email_warning = QLabel(self)
        self.email_warning.setStyleSheet("QLabel { color: red; }")
        self.morning_entry = QCheckBox(self)
        self.evening_entry = QCheckBox(self)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttons.button(QDialogButtonBox.Ok).setAutoDefault(False)
        self.buttons.button(QDialogButtonBox.Cancel).setDefault(True)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("First Name", self.first_name_entry)
        layout.addRow("Last Name", self.last_name_entry)
        layout.addRow("Email", self.email_entry)
        layout.addWidget(self.duplicate_notice)
        layout.addWidget(self.email_warning)
        layout.addRow("Morning", self.morning_entry)
        layout.addRow("Evening", self.evening_entry)
        layout.addRow(self.buttons)

        self.email_entry.textChanged.connect(self.validate_email)

    def validate_email(self, text):
        if not re.match(EMAIL_PATTERN, text):
            self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
            self.email_warning.setText("Invalid Email")
        else:
            self.buttons.button(QDialogButtonBox.Ok).setEnabled(True)
            self.email_warning.setText("")


#confirmation dialog for deleting an entry from the db
#requires list of IDs marked for removal
class DeleteCustomer(QDialog):
    def __init__(self, id_remove, parent=None):
        super().__init__()
        self.id_remove = id_remove

        self.setWindowTitle("Delete Customer")
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setAutoDefault(False)
        buttons.button(QDialogButtonBox.Cancel).setDefault(True)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        label = QLabel(self)
        layout.addWidget(label)

        label.setText(f"Delete {len(self.id_remove)} Customer(s)?")
        layout.addWidget(label)
        layout.addWidget(buttons)
        self.setLayout(layout)


class ImportCustomers(QDialog):
    def __init__(self, data_len, parent=None):
        super().__init__()
        self.setWindowTitle("Import From CSV")
        self.label = QLabel(self)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.morning_entry = QCheckBox(self)
        self.evening_entry = QCheckBox(self)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addWidget(self.label)
        self.label.setText(f"Importing {data_len} Customer(s). "
                           f"Duplicate emails will be ignored."
                           f"\nSelect applicable classes.")
        layout.addRow("Morning Classes", self.morning_entry)
        layout.addRow("Evening Classes", self.evening_entry)
        layout.addRow(self.buttons)
        self.setLayout(layout)

class DropTable(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Drop Table")
        self.label = QLabel(self)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setAutoDefault(False)
        self.buttons.button(QDialogButtonBox.Cancel).setDefault(True)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        self.label.setText("This will irreversibly erase all customer data from the database."
                           "\nAre you sure you want to continue?")
        layout.addWidget(self.label)
        layout.addWidget(self.buttons)

