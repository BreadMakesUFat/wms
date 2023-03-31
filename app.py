from flask import Flask, render_template, request, g
import csv 
import datetime
import os
import sqlite3

app = Flask(__name__)

# load config
app.config.from_object("config.DevelopmentConfig")

# open a database connection if needed
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DB_PATH'],
        )
        #g.db.row_factory = sqlite3.Row

    return g.db

# close the database connection if needed
def close_db(e=None):
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
@app.route("/wms/stock", methods=["GET"])
def route_stock():
    # retrieve data from db
    db = get_db()
    cur = db.cursor()
    query = cur.execute("SELECT * from stock")
    res = list(query)

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
        
        file = body.decode("utf-8")
        
        # TODO: INSERT into db
        
        return "Ok", 200

# run the server (only development!)
if __name__ == "__main__":
    app.run(
        host = app.config["HOST"],
        port = app.config["PORT"],
        debug = app.config["DEBUG"],
        ssl_context = "adhoc"
        )