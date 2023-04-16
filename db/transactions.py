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
    df = pd.read_csv(csvStringIO, sep=None)

    # drop unused columns
    df = df.iloc[:,:len(SCHEMA_STOCK)-1]

    # add missing columns
    n = df.shape[0]
    df["Date"] = [datetime.datetime.now().strftime("%Y-%m-%d")] * n

    # set schema
    df.columns = SCHEMA_STOCK.keys()
    df = df.reset_index(drop=True)
    # df = df.astype(SCHEMA_STOCK)

    # insert into database
    cur = db.cursor()
    try:
        df.to_sql(name="stock", con=db, if_exists="append", index=False)
        return True, "No errors"
    except Exception:
        return False, "Error"


# Class for filter queries
class StockFilter:

    query = "SELECT * FROM stock WHERE 1 = 1"
    params = []

    def __init__(self):
        pass

    def filterText(self, column, param):
        self.query += f" AND {column} LIKE ?"
        self.params.append(param)

    def filterNumber(self, column, operator, param):
        self.query += f" AND {column} {operator} ?"
        self.params.append(param)

    def filterDate(self, column, operator, date):
        d = datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
        self.query += f" AND {column} {operator} ?"
        self.params.append(d)

    def filterDateRange(self, column, date1, date2):
        d1 = datetime.datetime.strptime(date1, "%d.%m.%Y").strftime("%Y-%m-%d")
        d2 = datetime.datetime.strptime(date2, "%d.%m.%Y").strftime("%Y-%m-%d")
        self.query += f" AND {column} BETWEEN ? AND ?"
        self.params.append(d1)
        self.params.append(d2)

    def execute(self, db):
        cur = db.cursor()
        res = cur.execute(self.query, tuple(self.params))
        return list(res)
