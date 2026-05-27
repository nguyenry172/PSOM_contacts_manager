#database functionality for music school mailing list

import sqlite3

#creates customer table if one does not already exist. otherwise, does nothing
def create_table():
    db = sqlite3.connect("school.db")

    query = """
    CREATE TABLE IF NOT EXISTS school (
    customer_id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT NOT NULL CHECK (length(email) > 3),
    morning         BOOLEAN NOT NULL,
    evening         BOOLEAN NOT NULL,
    UNIQUE (email)
    );
    """

    cursor = db.cursor()
    cursor.execute(query)
    db.close()

def drop_table():
    with sqlite3.connect("school.db") as db:
        query = """
        DROP TABLE IF EXISTS school;
        """
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()

#imports data from Google Contacts CSV. Optional parameters to designate as morning or evening
def import_customers(data, morning=False, evening=False):
    create_table() #prevents importing into a db that doesn't exist
    data = [row + (morning, evening) for row in data]
    with sqlite3.connect("school.db") as db:
        cursor = db.cursor()
        cursor.executemany(
            """
            INSERT OR IGNORE INTO school (first_name, last_name, email, morning, evening)
            VALUES (?, ?, ?, ?, ?)
            """, data
        )
        db.commit()

def add_customer(first, last, email, morning=False, evening=False):
    db = sqlite3.connect("school.db")
    query = """
    INSERT OR IGNORE INTO school (first_name, last_name, email, morning, evening)
    VALUES (?, ?, ?, ?, ?)
    """
    cursor = db.cursor()
    cursor.execute(query, (first, last, email, morning, evening))
    db.commit()
    db.close()


# fetches customer data from db
# accepts an optional AM/PM filter.
# Calling without an argument shows all customers
def get_customers(e=None):
    query = "SELECT * FROM school"
    if e != "Filter":
        if e == "AM":
            query = "SELECT * FROM school WHERE morning = TRUE"
        if e == "PM":
            query = "SELECT * FROM school WHERE evening = TRUE"
    try:
        with sqlite3.connect('school.db') as db:
            cursor = db.cursor()
            cursor.execute(query)
            return cursor.fetchall()
    except sqlite3.OperationalError as e:
        print("Database error: ", e)
        return []



def update_customer(id, updated_first, updated_last, updated_email,
                    updated_morning=False, updated_evening=False):
    db = sqlite3.connect("school.db")

    query = """
    UPDATE school SET first_name = ?, last_name = ?, email = ?, morning = ?, evening = ?
    WHERE customer_id == ?
    """

    cursor = db.cursor()
    cursor.execute(query, (updated_first, updated_last, updated_email, updated_morning, updated_evening, id))
    db.commit()
    db.close()


def remove_customer(customer_id):
    db = sqlite3.connect("school.db")
    to_remove = ",".join(str(x) for x in customer_id)
    query = f"DELETE FROM school WHERE customer_id IN ({to_remove})"
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    db.close()