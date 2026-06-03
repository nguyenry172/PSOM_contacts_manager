#main ui and driver code for music school mailing list
import os
import re
from gc import enable

import db
import dialog
import BM_Match

import csv
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QWidget, QHBoxLayout, QAction, QVBoxLayout, QPushButton,
                             QCheckBox, QTableWidget, QDialog, QTableWidgetItem,
                             QHeaderView, QComboBox, QFileDialog, QToolTip, QMessageBox, QLineEdit)
from PyQt5.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        db.create_table()
        self.unsaved_changes = False
        self.modified_rows = set()
        self.rows = []
        self.load_db_data()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Petaluma Music School Mailing List")
        self.setWindowIcon(QIcon(resource_path('psom.jpg')))
        self.resize(700, 400)

        column_names = ["", "First Name", "Last Name", "Email", "AM", "PM"]

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        add_customer_button = QPushButton("Add Customer")
        add_customer_button.clicked.connect(self.add_customer_dialog)
        button_layout.addWidget(add_customer_button)

        delete_customer_button = QPushButton("Delete Customer")
        delete_customer_button.clicked.connect(self.delete_customer_dialog)
        button_layout.addWidget(delete_customer_button)

        self.copy_emails_button = QPushButton("Copy Emails")
        self.copy_emails_button.clicked.connect(self.copy_emails)
        button_layout.addWidget(self.copy_emails_button)

        self.filter_button = QComboBox()
        self.filter_button.addItems(["Filter", "AM", "PM"])
        self.filter_button.currentTextChanged.connect(self.render_table)
        button_layout.addWidget(self.filter_button)


        self.save_button = QPushButton("Save Changes", self)
        self.save_button.clicked.connect(self.save_changes)
        self.save_button.setShortcut("Ctrl+S")
        button_layout.addWidget(self.save_button)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(self.search)
        button_layout.addWidget(self.search_bar)


        #menu actions
        action_import_customer = QAction("Import Customers from CSV", self)
        action_import_customer.triggered.connect(self.import_customer_dialog)

        action_drop_table = QAction("Drop Table", self)
        action_drop_table.triggered.connect(self.drop_table_dialog)

        #menu ui
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        file_menu.addAction(action_import_customer)
        file_menu.addAction(action_drop_table)


        #main table UI
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(column_names)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # default for all columns
        # Override specific columns
        for col in (0, 4, 5):
            header.setSectionResizeMode(col, QHeaderView.Fixed)
        self.table.itemChanged.connect(self.item_changed)

        main_layout.addWidget(self.table)
        self.render_table(self.filter_button.currentText())


    #opens window to import customer data from Google Contacts csv
    def import_customer_dialog(self):
        csv_path, _ = QFileDialog.getOpenFileName(self, "Import Contacts", "", "CSV Files (*.csv)")
        if not csv_path:
            return

        data = []
        with open(csv_path) as csvfile:
            reader = csv.DictReader(csvfile)
            try:
                for row in reader:
                    data.append((row["First Name"], row["Last Name"], row["E-mail 1 - Value"]))
            except KeyError as e:
                dlg = QMessageBox()
                dlg.setIcon(QMessageBox.Warning)
                dlg.setWindowTitle("CSV Error")
                dlg.setText(f"Column not found in CSV: {e}")
                dlg.setStandardButtons(QMessageBox.Ok)
                dlg.exec_()
                return

        dlg = dialog.ImportCustomers(len(data))
        if dlg.exec_() == QDialog.Accepted:
            db.import_customers(data, dlg.morning_entry.isChecked(), dlg.evening_entry.isChecked())
            self.load_db_data()
            self.render_table(self.filter_button.currentText())


    #opens a window and prompts to enter data
    def add_customer_dialog(self):
        dlg = dialog.CreateRecord(self)
        if dlg.exec_() == QDialog.Accepted:
            first_name = dlg.first_name_entry.text()
            last_name = dlg.last_name_entry.text()
            email = dlg.email_entry.text()
            morning = dlg.morning_entry.isChecked()
            evening = dlg.evening_entry.isChecked()
            db.add_customer(first_name, last_name, email, morning, evening)
            self.load_db_data()
            self.render_table(self.filter_button.currentText())


    #confirmation window for customer deletion
    def delete_customer_dialog(self):
        id_remove = []

        for x in range(self.table.rowCount()):
            cur_row = self.table.cellWidget(x, 0)
            if cur_row.isChecked():
                id_remove.append(cur_row.property("ID"))
            print(id_remove)

        if not id_remove:
            return

        dlg = dialog.DeleteCustomer(id_remove)
        if dlg.exec_() == QDialog.Accepted:
            db.remove_customer(id_remove)
            self.load_db_data()
            self.render_table(self.filter_button.currentText())


    #confirmation window for dropping character db
    def drop_table_dialog(self):
        dlg = dialog.DropTable()
        if dlg.exec_() == QDialog.Accepted:
            db.drop_table()
            self.render_table(self.filter_button.currentText())


    #copies to clipboard emails from the QTableWidget
    #copies emails from selected rows. otherwise, copies from all currently displayed rows
    #formatted for pasting directly into a Gmail recipient list
    def copy_emails(self):
        selected_emails = []
        all_emails = []
        for i in range(self.table.rowCount()):
            if not self.table.isRowHidden(i):
                if self.table.cellWidget(i, 0).isChecked():
                    selected_emails.append(self.table.item(i, 3).text())
                all_emails.append(self.table.item(i, 3).text())

        if selected_emails:
            QApplication.clipboard().setText(", ".join(selected_emails))
            # print("Copying selected emails")
        else:
            QApplication.clipboard().setText(", ".join(all_emails))
            # print("Copying all emails")
        QToolTip.showText(self.copy_emails_button.mapToGlobal(self.copy_emails_button.rect().center()),
                          "Emails copied to clipboard")


    #marks modified rows for saving
    def item_changed(self, e):
        self.unsaved_changes = True
        row = e.row()
        c_id = self.table.cellWidget(row, 0).property("ID")
        # print(f"row: {row}, c_id: {c_id}")
        self.modified_rows.add(c_id)


    #updates the db to reflect changes made on the QTable
    def save_changes(self, close=False):
        skipped = 0

        for i in range(len(self.rows)):
            c_id = self.table.cellWidget(i, 0).property("ID")
            if c_id not in self.modified_rows:
                continue
            updated_first_name = self.table.item(i,1).text()
            updated_last_name = self.table.item(i,2).text()
            updated_email = self.table.item(i,3).text()
            if not re.match(dialog.EMAIL_PATTERN, updated_email):
                skipped += 1
                continue
            updated_am = self.table.cellWidget(i,4).isChecked()
            updated_pm = self.table.cellWidget(i,5).isChecked()
            db.update_customer(c_id, updated_first_name, updated_last_name, updated_email, updated_am, updated_pm)

        self.unsaved_changes = False
        if close:
            return
        msg = f"Changes saved ({skipped} invalid emails skipped)" if skipped else "Changes Saved"
        QToolTip.showText(self.save_button.mapToGlobal(self.save_button.rect().center()),
                          msg)
        self.load_db_data()
        self.render_table(self.filter_button.currentText())


    #uses boyer-moore pattern matching to find entries whose cells contain the search
    #hides all rows that do not match
    def search(self, query):
        if not query:
            self.render_table(self.filter_button.currentText())
        for i in range(self.table.rowCount()):
            row_contents = self.row_text(i)
            if not BM_Match.search(row_contents, query.lower()):
                self.table.setRowHidden(i, True)


    #helper function for search
    #returns concatenation of name and email columns of a given row
    #ignores case
    def row_text(self, row):
        text = ""
        for i in range(1, 4):
            text += self.table.item(row, i).text().lower()
        return text


    #loads db data into QTableWidget
    def load_db_data(self):
        self.rows = db.get_customers()


    #displays data loaded on table
    #accepts optional filter parameters
    def render_table(self, e=None):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.table.setSortingEnabled(True)

        if self.rows:
            for data in self.rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                checkbox_style = "margin-left: auto; margin-right: auto;"
                select_checkbox = QCheckBox()
                select_checkbox.setStyleSheet(checkbox_style)
                select_checkbox.setProperty("ID", data[0])  #customer ID is hidden as a property of the select checkbox
                self.table.setCellWidget(row, 0, select_checkbox)
                self.table.setItem(row, 1, QTableWidgetItem(data[1]))
                self.table.setItem(row, 2, QTableWidgetItem(data[2]))
                self.table.setItem(row, 3, QTableWidgetItem(data[3]))
                am_checkbox = QCheckBox(self)
                am_checkbox.setChecked(data[4])
                am_checkbox.setStyleSheet(checkbox_style)
                self.table.setCellWidget(row, 4, am_checkbox)
                pm_checkbox = QCheckBox(self)
                pm_checkbox.setChecked(data[5])
                pm_checkbox.setStyleSheet(checkbox_style)
                self.table.setCellWidget(row, 5, pm_checkbox)

                am_checkbox.stateChanged.connect(lambda _, c_id=data[0]: (self.modified_rows.add(c_id), setattr(self, 'unsaved_changes', True)))
                pm_checkbox.stateChanged.connect(lambda _, c_id=data[0]: (self.modified_rows.add(c_id), setattr(self, 'unsaved_changes', True)))

                if e == "AM":
                    self.table.setRowHidden(row, not am_checkbox.isChecked())
                elif e == "PM":
                    self.table.setRowHidden(row, not pm_checkbox.isChecked())
                else:
                    self.table.setRowHidden(row, False)

        self.table.blockSignals(False)


    def closeEvent(self, e):
        if self.unsaved_changes:
            dlg = QMessageBox(self)
            dlg.setIcon(QMessageBox.Warning)
            dlg.setWindowTitle("Unsaved Changes")
            dlg.setText("You have unsaved changes. Are you sure you want to quit?")
            dlg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            dlg.setDefaultButton(QMessageBox.Cancel)
            result = dlg.exec_()

            if result == QMessageBox.Save:
                self.save_changes(close=True)
                self.unsaved_changes = False
                e.accept()
            elif result == QMessageBox.Discard:
                e.accept()
            else:
                e.ignore()
        else:
            e.accept()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)




def main(test=False):
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ =="__main__":
    main(test=False)