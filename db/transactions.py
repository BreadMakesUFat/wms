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

translate_unit = {
    "STÜCK": "Կտոր",
    "KG": "կգ"
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

    # set new columns
    data["BODescription"] = None 
    data["ArticleDescriptionTranslated"] = None 
    data["UnitTranslated"] = translate_unit.get(data["unit"].upper().strip(), None)
    data["GovernmentCode"] = None
    data["PricePerUnit"] = None

    try:
        # bon is given
        if bon:

            # get article id, description, price
            cur.execute("SELECT ArticleID, ArticleDescription, Amount, Price, BODescription  from stock WHERE BON = ?", (bon,))
            res = cur.fetchone()
            if res:
                data["articleID"] = res[0]
                data["articleDescription"] = res[1]
                price = res[3]
                data["PricePerUnit"] = price
                data["BODescription"] = res[4]
            else:
                print("the given bon does not have an existing articleID in stock!")
                return False
            
            # get translations
            articleID = data.get("articleID", "")
            cur.execute("SELECT ArticleDescription, GovernmentCode FROM articleTranslations WHERE ArticleID = ?", (articleID, ))
            res = cur.fetchone()
            if res:
                data["ArticleDescriptionTranslated"] = res[0]
                data["GovernmentCode"] = res[1]
    
        # get info
        elif articleID:
            cur.execute("SELECT ArticleDescription, BON, BODescription, Amount, Price from stock WHERE ArticleID = ?", (articleID,))
            res = cur.fetchone()
            if res:
                data["articleDescription"] = res[0]
                data["bon"] = res[1]
                data["BODescription"] = res[2]
                price = res[4]
                data["PricePerUnit"] = price
            else:
                print("the given article id does not exist in stock!")
                return False
            # find translations 
            query = "SELECT ArticleDescription, GovernmentCode FROM articleTranslations WHERE ArticleID = ?"
            params = (articleID, )
            cur.execute(query, params)
            translations = cur.fetchone()
            if translations:
                articleDescription = translations[0]
                governmentCode = translations[1]
                data["ArticleDescriptionTranslated"] = articleDescription 
                data["GovernmentCode"] = governmentCode


        # subtract from stock
        query = "UPDATE stock SET Amount = Amount - ? WHERE BON = ?"
        parameters = (
            data["amount"],
            data["bon"]
        )

        db.execute(query, parameters)

        # write to deliveries table
        query = "INSERT INTO deliveries (BON, BODescription, ArticleID, ArticleDescription, ArticleDescriptionTranslated, Destination, Recipient, Amount, Unit, UnitTranslated, Date, GovernmentCode, PricePerUnit) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        parameters = (
        data["bon"],
        data["BODescription"],
        data["articleID"],
        data["articleDescription"],
        data["ArticleDescriptionTranslated"],
        data["destination"],
        data["recipient"],
        data["amount"],
        data["unit"],
        data["UnitTranslated"],
        data["date"],
        data["GovernmentCode"],
        data["PricePerUnit"]
        )

        db.execute(query, parameters)
        db.commit()
        return True

    except Exception as e:
        print(e)
        return False


def edit_deliveries(db, data):
    query = "UPDATE deliveries SET BON = ?, BODescription = ?, ArticleID = ?, ArticleDescription = ?, ArticleDescriptionTranslated = ?, Destination = ?, Recipient = ?, Amount = ?, Unit = ?, UnitTranslated = ?, Date = ?, GovernmentCode = ?, PricePerUnit = ? WHERE ID = ?"
    parameters = (
        data["bon"],
        data["boDescription"],
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

    # add columns
    df["BODescription"] = None 
    df["ArticleDescriptionTranslated"] = None 
    df["UnitTranslated"] = None 
    df["GovernmentCode"] = None 
    df["PricePerUnit"] = None 

    try:

        # iterate over all rows
        for i,row in df.iterrows():
            df.at[i, "UnitTranslated"] = translate_unit.get(row["Unit"].upper().strip(), None)
            # bon is given
            if row["BON"]:
                query = "SELECT ArticleID, ArticleDescription, Amount, Price, BODescription FROM stock WHERE BON = ?"
                params = (row["BON"], )
                cur = db.cursor()
                cur.execute(query, params)
                res = cur.fetchone()
                if res:
                    articleID = res[0]
                    articleDescription = res[1]
                    price = res[3]
                    df.at[i, "ArticleID"] = articleID 
                    df.at[i, "ArticleDescription"] = articleDescription
                    df.at[i, "PricePerUnit"] = price
                    df.at[i, "BODescription"] = res[4]
                    # find translations 
                    query = "SELECT ArticleDescription, GovernmentCode FROM articleTranslations WHERE ArticleID = ?"
                    params = (articleID, )
                    cur.execute(query, params)
                    translations = cur.fetchone()
                    if translations:
                        articleDescription = translations[0]
                        governmentCode = translations[1]
                        df.at[i, "ArticleDescriptionTranslated"] = articleDescription 
                        df.at[i, "GovernmentCode"] = governmentCode

            elif row["ArticleID"]:
                    articleID = row["ArticleID"]
                    # find article description
                    query = "SELECT ArticleDescription, BON, BODescription, Amount, Price FROM stock WHERE ArticleID = ?"
                    params = (articleID, )
                    cur = db.cursor()
                    cur.execute(query, params)
                    res = cur.fetchone()
                    if res:
                        articleDescription = res[0]
                        df.at[i, "BON"] = res[1]
                        df.at[i, "BODescription"] = res[2]
                        price = res[4]
                        df.at[i, "ArticleDescription"] = articleDescription
                        df.at[i, "PricePerUnit"] = price
                    # find translations
                    query = "SELECT ArticleDescription, GovernmentCode FROM articleTranslations WHERE ArticleID = ?"
                    params = (articleID, )
                    cur.execute(query, params)
                    translations = cur.fetchone()
                    if translations:
                        articleDescription = translations[0]
                        governmentCode = translations[1]
                        df.at[i, "ArticleDescriptionTranslated"] = articleDescription 
                        df.at[i, "GovernmentCode"] = governmentCode


        # subtract amount from stock
        for i,row in df.iterrows():
            params = (
                row["Amount"],
                row["BON"]
            )
            query = "UPDATE stock SET Amount = Amount - ? WHERE BON = ?"
            db.execute(query, params)
        db.commit()


        # add to deliveries
        df.to_sql(name="deliveries", con=db, if_exists="append", index=False)
        return True, "No errors"
    except Exception as e:
        print(e)
        return False, "Error"
    
def get_deliveries(db, params=("Key",)):
    cur = db.cursor()
    query = "SELECT * FROM deliveries ORDER BY ? DESC"
    res = cur.execute(query, params)
    return list(res)