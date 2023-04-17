import pandas as pd
import datetime
from io import StringIO

# Constants
SCHEMA_STOCK = { 
    "ArticleID": str,
    "ArticleDescription": str,
    "BON": str,
    "BODescription": str, 
    "BestBefore": str, 
    "Amount": int, 
    "Location": str,
    "Weight": float,
    "Unit": str, 
    "Price": float, 
    "Date": str
    }

# Stock
def get_stock(db, params=("Date",)):
    cur = db.cursor()
    query = "SELECT * FROM stock ORDER BY ? ASC"
    res = cur.execute(query, params)
    return list(res)

def import_stock(db, file):
    # create dataframe from csv string
    csvStringIO = StringIO(file)
    df = pd.read_csv(csvStringIO, sep=None, decimal=",", thousands=".", engine="python", parse_dates=[4], dayfirst=True)

    # drop unused columns
    df = df.iloc[:,:len(SCHEMA_STOCK)-1]

    # add missing columns
    n = df.shape[0]
    df["Date"] = [datetime.datetime.now().strftime("%Y-%m-%d")] * n

    # set schema
    df.columns = SCHEMA_STOCK.keys()
    df = df.reset_index(drop=True)
    df = df.astype(SCHEMA_STOCK)
    df["BestBefore"] = df["BestBefore"].replace("NaT", None)

    # insert into database
    cur = db.cursor()
    try:
        df.to_sql(name="stock", con=db, if_exists="append", index=False)
        return True, "No errors"
    except Exception:
        return False, "Error"


# Class for filter queries
class StockFilter:

    def __init__(self):
        self.query = "SELECT * FROM stock WHERE 1 = 1"
        self.params = []

    def filterText(self, column, param):
        self.query += f" AND {column} LIKE ?"
        self.params.append(param)

    def filterNumber(self, column, operator, param):
        self.query += f" AND {column} {operator} ?"
        self.params.append(param)

    def filterDate(self, column, operator, date):
        self.query += f" AND {column} {operator} ?"
        self.params.append(date)

    def execute(self, db):
        cur = db.cursor()
        res = cur.execute(self.query, tuple(self.params))
        return list(res)


# Barcode Scanner
def new_delivery(db, df):
    df = df.reset_index(drop=True)

    # insert into database
    cur = db.cursor()
    try:
        df.to_sql(name="deliveries", con=db, if_exists="append", index=False)
        return True, "No errors"
    except Exception:
        return False, "Error"
    
def get_deliveries(db, params=("Key",)):
    cur = db.cursor()
    query = "SELECT * FROM deliveries ORDER BY ? DESC"
    res = cur.execute(query, params)
    return list(res)