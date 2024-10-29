import sqlite3
import sys

from config import CONFIG

class ReservationDB:
    @staticmethod
    def initialize(database_connection: sqlite3.Connection):
        cursor = database_connection.cursor()
        try:
            print("Dropping existing tables (if present)...")
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS reservations")
            cursor.execute("DROP TABLE IF EXISTS accommodations")
            cursor.execute("DROP TABLE IF EXISTS bookings")
            cursor.execute("DROP TABLE IF EXISTS transactions")
        except sqlite3.OperationalError as db_error:
            print(f"Unable to drop table. Error: {db_error}")
        print("Creating tables...")
        cursor.execute(ReservationDB.CREATE_TABLE_USERS)
        cursor.execute(ReservationDB.CREATE_TABLE_RESERVATIONS)
        cursor.execute(ReservationDB.CREATE_TABLE_ACCOMMODATIONS)
        cursor.execute(ReservationDB.CREATE_TABLE_BOOKINGS)
        cursor.execute(ReservationDB.CREATE_TABLE_TRANSACTIONS)
        database_connection.commit()
        
        print("Populating database with sample data...")
        cursor.executemany(ReservationDB.INSERT_ACCOMMODATIONS, ReservationDB.sample_accommodation)
        database_connection.commit()
        
    CREATE_TABLE_USERS = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )"""

    CREATE_TABLE_RESERVATIONS = """
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        reservation_date DATE NOT NULL,
        time_slot TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )"""

    CREATE_TABLE_ACCOMMODATIONS = """
    CREATE TABLE IF NOT EXISTS accommodations (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT NOT NULL, 
        address TEXT NOT NULL, 
        price REAL NOT NULL, 
        capacity INTEGER NOT NULL 
    )"""

    CREATE_TABLE_BOOKINGS = """
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        room_name TEXT NOT NULL, 
        start_date TEXT NOT NULL, 
        end_date TEXT NOT NULL,
        total_cost REAL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )"""

    CREATE_TABLE_TRANSACTIONS = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER, 
        is_paid TEXT NOT NULL, 
        payment_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
    )"""

     
    INSERT_ACCOMMODATIONS = "INSERT INTO accommodations VALUES (?, ?, ?, ?, ?)"
    
    sample_accommodation = [
        (1, "Splash Suite", "Aqua Lane 102", "60", "3"),
        (2, "Wave Villa", "Golflaan 302", "75", "5"),
        (3, "Cabana Bungalow", "Zeestraat 24", "55", "2"),
        (4, "Piraten Cove", "Aargh 11", "60", "3"),
        (5, "Sunset Retreat", "Sunset View 44", "100", "6"),
        (6, "Tropical Bungalow", "Tropical Water 55", "40", "2"),
        (7, "Sonesta Villa", "Crystal Clear Water 420", "80", "8"),
        (8, "Garden Hideaway", "Super Secret 590", "35", "2")
    ]
#take a form translate to database design --> normaliseren
#on cascade is what happens the table updates on the different tables associated with a value, on delete restrict can't delete it if other values depend on it

def main():
    db_conn = sqlite3.connect(CONFIG["database"]["name"])
    db_conn.row_factory = sqlite3.Row
    
    ReservationDB.initialize(db_conn)
    db_conn.close()
    
    print("Database creation finished!")
    return 0

if __name__ == "__main__":
    sys.exit(main())