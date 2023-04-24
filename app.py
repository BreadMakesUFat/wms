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
app.config.from_object("config.DevelopmentConfig")

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
    articleDescriptions = [""] * n

    for i,v in enumerate(data["bons"]):
        if (v.startswith("AT")):
            articleIDs[i] = v 
        else:
            bons[i] = v

    d = {
        "BON": bons,
        "ArticleID": articleIDs,
        "ArticleDescription": articleDescriptions,
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

# stock
@app.route("/wms/stock/", methods=["GET"])
def route_stock():

    if request.method == "GET":
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
            if len(bon.split(",")) < 2:
                bon = bon + "%" if bon else bon 
                filter.filterText("BON", bon)
            else:
                bons = bon.split(",")
                bons = [f"{b.strip()}" for b in bons]
                filter.filterBons(bons)
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
        res2 = [
            sum([r["Amount"] if r["Amount"] else 0 for r in res]),
            sum([r["Weight"] if r["Weight"] else 0 for r in res]),
            sum([r["Price"] if r["Price"] else 0 for r in res])
        ]

        return render_template("wms_stock.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"], result = res, sums = res2)

@app.route("/wms/edit_stock/", methods=["GET", "POST"])
def route_edit_stock():
    if request.method == "GET":
        params = request.args
        return render_template("wms_stock_edit.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"], fields = params)
    elif request.method == "POST":
        data = dict(request.get_json())

        # replace empty strings with None
        for k,v in data.items():
            if v == "":
                data[k] = None 

        db = get_db()
        res = transactions.edit_stock(db, data)
        if res:
            return "Ok", 200
        else:
            return "Error", 400
        
@app.route("/wms/delete_stock/", methods=["POST"])
def route_delete_stock():
    data = request.get_json()   
    db = get_db()
    res = transactions.delete_stock(db, data["bon"])
    if res:
        return "Ok", 200
    else:
        return "Error", 400         

# csv import
@app.route("/wms/import/", methods=["GET", "POST"])
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
        # file = body.decode("utf-8")  

        # append dataframe to database
        db = get_db()
        ok, err = transactions.import_stock(db, file)
        
        # response to client
        if ok:
            return "Ok", 200
        else:
            return "An error occured. The file might contain BON ids that are already used!", 400
    
@app.route("/wms/new_delivery/", methods=["GET", "POST"])
def route_new_delivery():
    if request.method == "GET":
        return render_template("wms_new_delivery.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"])
    elif request.method == "POST":
        # read data 
        data = dict(request.get_json())
        data["date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # replace empty fields with None 
        for k,v in data.items():
            if v == "":
                data[k] = None 
        
        # parse id 
        id = data["id"]
        if id.startswith("AT"):
            data["articleID"] = id 
            data["bon"] = None 
        else:
            data["bon"] = id 
            data["articleID"] = None
            
        db = get_db()
        res = transactions.new_single_delivery(db, data)

        if res:        
            return "Ok", 200
        else:
            return "Error", 400
    
@app.route("/wms/deliveries/", methods=["GET"])
def route_deliveries():

    # get fields
    key1 = request.args.get("key1", None) 
    key2 = request.args.get("key2", None)
    bon = request.args.get("bon", None)
    articleID = request.args.get("articleID", None)
    articleDescription = request.args.get("articleDescription", None)
    destination = request.args.get("destination", None)
    recipient1 = request.args.get("recipient1", None)
    recipient2 = request.args.get("recipient2", None)
    amount1 = request.args.get("amount1", None)
    amount2 = request.args.get("amount2", None)
    unit = request.args.get("unit", None)
    date1 = request.args.get("date1", None)
    date2 = request.args.get("date2", None)

    # parse 
    key1 = int(key1) if key1 else key1 
    key2 = int(key2) if key2 else key2
    articleID = articleID + "%" if articleID else articleID
    articleDescription = articleDescription + "%" if articleDescription else articleDescription 
    destination = destination + "%" if destination else destination
    recipient1 = int(recipient1) if recipient1 else recipient1 
    recipient2 = int(recipient2) if recipient2 else recipient2
    amount1 = int(amount1) if amount1 else amount1
    amount2 = int(amount2) if amount2 else amount2
    unit = unit + "%" if unit else unit 

    # add filters
    db = get_db()
    filter = transactions.DeliveriesFilter()

    if key1:
        filter.filterNumber("ID", ">=", key1)
    if key2:
        filter.filterNumber("ID", "<=", key2)
    if bon:
        if len(bon.split(",")) < 2:
            bon = bon + "%" if bon else bon 
            filter.filterText("BON", bon)
        else:
            bons = bon.split(",")
            bons = [f"{b.strip()}" for b in bons]
            filter.filterBons(bons)
    if articleID:
        filter.filterText("ArticleID", articleID)
    if articleDescription:
        filter.filterText("ArticleDescription", articleDescription)
    if destination:
        filter.filterText("Destination", destination)
    if recipient1:
        filter.filterNumber("Recipient", ">=", recipient1)
    if recipient2:
        filter.filterNumber("Recipient", "<=", recipient2)
    if amount1:
        filter.filterNumber("Amount", ">=", amount1)
    if amount2:
        filter.filterNumber("Amount", "<=", amount2)
    if unit:
        filter.filterText("Unit", unit)
    if date1:
        filter.filterDate("Date", ">=", date1)
    if date2:
        filter.filterDate("Date", "<=", date2)

    res = filter.execute(db)

    return render_template("wms_deliveries.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"], result=res)

@app.route("/wms/edit_deliveries/", methods=["GET", "POST"])
def route_edit_deliveries():
    if request.method == "GET":
        params = request.args 
        return render_template("wms_deliveries_edit.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"], fields = params)
    elif request.method == "POST":
        data = dict(request.get_json())

        # replace empty strings with None 
        for k,v in data.items():
            if v == "":
                data[k] = None 

        db = get_db()
        res = transactions.edit_deliveries(db, data)
        if res:
            return "Ok", 200
        else:
            return "Error", 400
        
@app.route("/wms/delete_delivery/", methods=["POST"])
def route_delete_delivery():
    data = request.get_json()
    db = get_db()
    res = transactions.delete_delivery(db, data["id"])
    if res:
        return "OK", 200
    else:
        return "Error", 400


# run the server (only development!) 
if __name__ == "__main__":
    app.run(
        host = app.config["HOST"],
        port = app.config["PORT"],
        debug = app.config["DEBUG"],
        ssl_context = "adhoc"
        )