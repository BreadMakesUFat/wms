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

# index
@app.route("/wms/", methods=["GET"])
def route_index():
    return render_template("wms_index.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"])

# stock
@app.route("/wms/stock", methods=["GET", "POST"])
def route_stock():
    if request.method == "GET":
        # retrieve data from db
        db = get_db()
        res = transactions.get_stock(db)

        # return data to client
        return render_template("wms_stock.j2", org_name = app.config["ORG_NAME"], org_id = app.config["ORG_ID"], result = res)

    elif request.method == "POST":
        # read filters
        pass

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