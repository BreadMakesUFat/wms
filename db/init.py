import sqlite3

DB_NAME = "booking_test.db"
SQL_SCRIPT = """
BEGIN;

DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS deliveries;

CREATE TABLE stock (
    BON INTEGER PRIMARY KEY,
    ID TEXT NOT NULL,
    Description TEXT NOT NULL,
    Batch TEXT NOT NULL,
    BatchDescription TEXT, 
    BestBefore TEXT,
    Amount INTEGER NOT NULL, 
    Unit TEXT NOT NULL, 
    Weight INTEGER NOT NULL, 
    Price TEXT NOT NULL
);

CREATE TABLE deliveries (
    ID TEXT PRIMARY KEY, 
    BON INTEGER NOT NULL, 
    Description TEXT NOT NULL,
    Amount INTEGER NOT NULL, 
    Destination TEXT NOT NULL, 
    Batch TEXT NOT NULL,
    NumberPersons INTEGER NOT NULL
);

COMMIT;
"""

if __name__ == "__main__":
    try:
        db = sqlite3.connect(DB_NAME)
        db.row_factory = sqlite3.Row 
        cur = db.cursor()
        cur.executescript(SQL_SCRIPT)   

        # close connection
        db.close()
    except:
        print("Error initialising the database")
        if db is not None:
            db.close()

