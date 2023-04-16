from flask import Flask, render_template, request, g
from io import StringIO
import db.transactions as transactions
import csv 
import datetime
import os
import sqlite3
import pandas as pd

app = Flask(__name__)

# load config
app.config.from_object("config.ProductionConfig")

# open a database connection if needed
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DB_PATH'],
        )
        g.db.row_factory = sqlite3.Row

    return g.db

# close the database connection if connection ends
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)

    if db is not None:
        db.close()


#########################################
############## Routes ###################
#########################################

# Barcode Scanner
@app.route("/barcode/", methods=["GET"])
def route_barcode_index():
    return render_template("barcode_index.j2", size = app.config["SCANNER_BOX"])

# Barcode bookings
@app.route("/barcode/bookings/", methods=["POST"])
def route_barcode_bookings():
    # check if fields exist 
    data = request.get_json()

    if "bons" not in data or "destination" not in data or "recipients" not in data or "amounts" not in data or "units" not in data:
        print(data)
        return "Missing data", 400 

    # fetch data from request
    n = len(data["bons"])

    bons = [""] * n 
    articleIDs = [""] * n

    for i,v in enumerate(data["bons"]):
        if (v.startswith("AT")):
            articleIDs[i] = v 
        else:
            bons[i] = v

    d = {
        "BON": bons,
        "ArticleID": articleIDs,
        "Destination": [data["destination"]] * n,
        "Recipient": data["recipients"],
        "Amount": data["amounts"],
        "Unit": data["units"],
        "Date": [datetime.datetime.now().strftime("%Y-%m-%d")] * n,
    }

    df = pd.DataFrame.from_dict(d)
    db = get_db()
    succ, err = transactions.new_delivery(db, df)

    if succ:
        return "OK", 200
    else:
        return "Err", 400

# WMS index
@app.route("/wms/", methods=["GET"])
def route_index():
    return render_template("wms_index.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"])

@app.route("/wms/stock/filter", methods=["GET"])
def route_stock_filter():
    # get fields
    articleID = request.args.get("articleID", None) 
    articleDescription = request.args.get("articleDescription", None)
    bon = request.args.get("bon", None)
    boDescription = request.args.get("boDescription", None)
    bestBefore1 = request.args.get("bestBefore1", None)
    bestBefore2 = request.args.get("bestBefore2", None)
    amount1 = request.args.get("amount1", None)
    amount2 = request.args.get("amount2", None)
    loc = request.args.get("loc", None)
    weight1 = request.args.get("weight1", None)
    weight2 = request.args.get("weight2", None)
    unit = request.args.get("unit", None)
    price1 = request.args.get("price1", None)
    price2 = request.args.get("price2", None)
    date1 = request.args.get("date1", None)
    date2 = request.args.get("date2", None)

    # parse
    articleID = articleID + "%" if articleID else articleID
    articleDescription = articleDescription + "%" if articleDescription else articleDescription
    bon = bon + "%" if bon else bon 
    boDescription = boDescription + "%" if boDescription else boDescription
    amount1 = int(amount1) if amount1 else amount1
    amount2 = int(amount2) if amount2 else amount2
    loc = loc + "%" if loc else loc 
    weight1 = float(weight1) if weight1 else weight1 
    weight2 = float(weight2) if weight2 else weight2
    price1 = float(price1) if price1 else price1
    price2 = float(price2) if price2 else price2

    # add filters
    db = get_db()
    filter = transactions.StockFilter()

    if articleID:
        filter.filterText("ArticleID", articleID)
    if articleDescription:
        filter.filterText("ArticleDescription", articleDescription)
    if bon:
        filter.filterText("BON", bon)
    if boDescription:
        filter.filterText("BODescription", boDescription)
    if bestBefore1:
        filter.filterDate("BestBefore", ">=", bestBefore1)
    if bestBefore2:
        filter.filterDate("BestBefore", "<=", bestBefore2)
    if amount1:
        filter.filterNumber("Amount", ">=", amount1)
    if amount2:
        filter.filterNumber("Amount", "<=", amount2)
    if loc:
        filter.filterText("Location", loc)
    if weight1:
        filter.filterNumber("Weight", ">=", weight1)
    if weight2:
        filter.filterNumber("Weight", "<=", weight2)
    if unit:
        filter.filterText("Unit", unit)
    if price1:
        filter.filterNumber("Price", ">=", price1)
    if price2:
        filter.filterNumber("Price", "<=", price2)
    if date1:
        filter.filterDate("Date", ">=", date1)
    if date2:
        filter.filterDate("Date", "<=", date2)

    res = filter.execute(db)

    return render_template("wms_stock.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"], result = res)


# stock
@app.route("/wms/stock", methods=["GET"])
def route_stock():
    # retrieve data from db
    db = get_db()
    res = transactions.get_stock(db)

    # return data to client
    return render_template("wms_stock.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"], result = res)
        

# csv import
@app.route("/wms/import", methods=["GET", "POST"])
def route_import():
    if request.method == "GET":
        return render_template("wms_import.j2")
    elif request.method == "POST":

        # csv file
        body = request.data
        
        # no file found
        if not body:
            return "Error: Missing data", 400
        
        # decode data
        file = body.decode("cp1252")      

        # append dataframe to database
        db = get_db()
        ok, err = transactions.import_stock(db, file)
        
        # response to client
        if ok:
            return "Ok", 200
        else:
            return "An error occured. The file might contain BON ids that are already used!", 400
    
@app.route("/wms/new_delivery", methods=["GET", "POST"])
def route_new_delivery():
    if request.method == "GET":
        return render_template("wms_new_delivery.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"])
    elif request.method == "POST":
        # read data 
        body = request.json
        # print(f"BON: {body['b_bon']}\nDestination: {body['b_dest']}\nRecipient: {body['b_rec']}\nAmount: {body['b_amount']}\nUnit: {body['b_unit']}")
        with get_db.cursor() as cur:
            # TODO: add to db
            pass
        return "Ok", 200
    
@app.route("/wms/deliveries", methods=["GET", "POST"])
def route_deliveries():
    if request.method == "GET":
        return render_template("wms_deliveries.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"], result=None)
    elif request.method == "POST":
        # TOOD: handle filters + add result query to render_template
        pass

# run the server (only development!)
if __name__ == "__main__":
    app.run(
        host = app.config["HOST"],
        port = app.config["PORT"],
        debug = app.config["DEBUG"],
        ssl_context = "adhoc"
        )