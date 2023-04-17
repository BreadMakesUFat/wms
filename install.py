import os 
import sqlite3

def install_dependencies():
    os.system("pip install -r dependencies.txt")

def init_db():
    DB_NAME = "db/booking_test.db"
    SCRIPT_PATH = "db/schema.sql"
    with open(SCRIPT_PATH, "r") as f:
        try:
            script = f.read()
            db = sqlite3.connect(DB_NAME)
            db.row_factory = sqlite3.Row 
            cur = db.cursor()
            cur.executescript(script)   

            # close connection
            db.close()
            print("finished initialising the db")
        except:
            if db is not None:
                db.close()

def create_config():
    with open("config.py", "w") as f:
        f.writelines([
            "class DevelopmentConfig(object):\n",
            "   DEBUG = True\n", 
            "   DEVELOPMENT = True\n", 
            "   SCANNER_BOX = (550, 150)\n",
            "   HOST = \n",
            "   PORT = 8000\n", 
            "   DB_PATH = 'db/booking_test.db'\n", 
            "   ORG_NAME = 'GAiN'\n"
            "   ORG_ID = 'Argenia'\n", 
            "\n",
            "\n",
            "class ProductionConfig(object):\n",
            "   DEBUG = False\n", 
            "   DEVELOPMENT = False\n", 
            "   SCANNER_BOX = (550, 150)\n",
            "   HOST = \n",
            "   PORT = 8000\n", 
            "   DB_PATH = 'db/booking_test.db'\n", 
            "   ORG_NAME = 'GAiN'\n"
            "   ORG_ID = 'Argenia'\n", 
        ])


if __name__ == "__main__":
    print("Installing dependencies:")
    install_dependencies()
    print("Initializing the database")
    init_db()
    print("Creating the config file")
    create_config()
    print("finished")