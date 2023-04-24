import sqlite3

DB_NAME = "../booking_test.db"
SCRIPT_PATH = "deliveries.sql"

if __name__ == "__main__":
    with open(SCRIPT_PATH, "r") as f:
        try:
            script = f.read()
            db = sqlite3.connect(DB_NAME)
            cur = db.cursor()
            cur.executescript(script)   

            # close connection
            db.close()
        except:
            print("Error initialising the database")
            if db is not None:
                db.close()
