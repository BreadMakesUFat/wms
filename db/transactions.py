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

    # replace "None" wit None 
    df = df.replace("None", None)

    # drop invalid rows w/o valid BON
    # e.g.: export has summe column
    df = df[df['ArticleID'] != "Summe"]

    try:
        df.to_sql(name="stock", con=db, if_exists="append", index=False)
        return True, "No errors"
    except Exception:
        return False, "Error"
    
def edit_stock(db, values):
    # build parameterized query
    query = "UPDATE stock SET ArticleID = ?, ArticleDescription = ?, BODescription = ?, BestBefore = ?, Amount = ?, Location = ?, Weight = ?, Unit = ?, Price = ?, Date = ? WHERE BON = ?"
    parameters = (
        values["articleID"],
        values["articleDescription"], 
        values["boDescription"], 
        values["bestBefore"], 
        values["amount"], 
        values["loc"], 
        values["weight"], 
        values["unit"], 
        values["price"], 
        values["date"], 
        values["bon"]
        )
    # update database 
    try:
        db.execute(query, parameters)
        db.commit()
        return True 
    except Exception as e:
        print(e)
        return False


def delete_stock(db, bon):
    query = "DELETE FROM stock WHERE BON = ?"
    params = (bon,)

    try:
        db.execute(query, params)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False

# Class for filter queries
class StockFilter:

    def __init__(self):
        self.query1 = "SELECT * FROM stock WHERE 1 = 1"
        self.params = []

    def filterText(self, column, param):
        s = f" AND {column} LIKE ?"
        self.query1 += s
        self.params.append(param)

    def filterNumber(self, column, operator, param):
        s = f" AND {column} {operator} ?"
        self.query1 += s
        self.params.append(param)

    def filterBons(self, bons):
        p = ["?"] * len(bons)
        p = ", ".join(p)
        s = f" AND BON IN ({p})"
        self.query1 += s
        self.params += bons

    def filterDate(self, column, operator, date):
        s = f" AND {column} {operator} ?"
        self.query1 += s
        self.params.append(date)

    def execute(self, db):
        cur = db.cursor()
        res = cur.execute(self.query1, tuple(self.params))
        return list(res)
    
# Deliveries
class DeliveriesFilter:

    def __init__(self):
        self.query = "SELECT * FROM deliveries WHERE 1 = 1"
        self.params = []

    def filterText(self, column, param):
        self.query += f" AND {column} LIKE ?"
        self.params.append(param)

    def filterNumber(self, column, operator, param):
        self.query += f" AND {column} {operator} ?"
        self.params.append(param)

    def filterBons(self, bons):
        p = ["?"] * len(bons)
        p = ", ".join(p)
        s = f" AND BON IN ({p})"
        self.query += s
        self.params += bons

    def filterDate(self, column, operator, date):
        self.query += f" AND {column} {operator} ?"
        self.params.append(date)

    def execute(self, db):
        cur = db.cursor()
        res = cur.execute(self.query, tuple(self.params))
        return list(res)
    
def new_single_delivery(db, data):

    cur = db.cursor()
    bon = data["bon"]
    articleID = data["articleID"]
    
    # bon is given
    if bon:
        res = cur.execute("SELECT ArticleID, ArticleDescription, Amount, Unit from stock WHERE BON = ?", (bon,)).fetchall()
        if res:
            data["articleID"] = res[0][0]
            data["articleDescription"] = res[0][1]

        else:
            return False
    
    # TODO: get info (translations, articleID, pricePerUnit)
    # TODO: subtract amount from database
    if articleID:
        res = cur.execute("SELECT ArticleDescription from stock WHERE ArticleID = ?", (articleID,)).fetchall()
        if res:
            data["articleDescription"] = res[0][0]

    query = "INSERT INTO deliveries (BON, ArticleID, ArticleDescription, Destination, Recipient, Amount, Unit, Date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    parameters = (
        data["bon"],
        data["articleID"],
        data["articleDescription"],
        data["destination"],
        data["recipient"],
        data["amount"],
        data["unit"],
        data["date"]
    )

    db.execute(query, parameters)
    db.commit()
    return True

def edit_deliveries(db, data):
    query = "UPDATE deliveries SET BON = ?, ArticleID = ?, ArticleDescription = ?, ArticleDescriptionTranslated = ?, Destination = ?, Recipient = ?, Amount = ?, Unit = ?, UnitTranslated = ?, Date = ?, GovernmentCode = ?, PricePerUnit = ? WHERE ID = ?"
    parameters = (
        data["bon"],
        data["articleID"],
        data["articleDescription"],
        data["articleDescriptionTranslated"],
        data["destination"],
        data["recipient"],
        data["amount"],
        data["unit"],
        data["unitTranslated"],
        data["date"],
        data["governmentCode"],
        data["pricePerUnit"],
        data["key"],
    )
    try:
        db.execute(query, parameters)
        db.commit()
        return True 
    except Exception as e:
        print(e)
        return False 
    
def delete_delivery(db, id):
    query = "DELETE FROM deliveries WHERE ID = ?"
    params = (id,)

    try:
        db.execute(query, params)
        db.commit()
        return True 
    except Exception as e:
        print(e)
        return False

# Barcode Scanner
def new_delivery(db, df):
    df = df.reset_index(drop=True)

    # TODO: get info + subtract from db
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