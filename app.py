# TODO: enter as OK in barcode window ----- Testing
# TODO: autofocus input fields ----- Testing
# TODO: add additional window after trying to upload changes (ok and retry options) ----- Testing
# TODO: create csv directory in start if needed 

from flask import Flask, render_template, request
import csv 
import datetime
import os
import time

app = Flask(__name__)

# load config
app.config.from_object("config.DevelopmentConfig")

def get_filename():
    return "csv/" + datetime.datetime.now().strftime("%Y-%m-%d") + ".csv"

# Create csv file for current day iff it doesnt exist already
def init_csv():
    file_name = get_filename()
    header = ["BON", "Destination", "No. of recipient", "Amount", "Unit", "Date", "Time"]
    if not os.path.exists(file_name):
        with open(file_name, "a") as file:
                writer = csv.writer(file)
                writer.writerow(header)

# initialize csv on start
init_csv()

# Routes
@app.route("/", methods=["GET"])
def route_index():
    return render_template("index.j2", size = app.config["SCANNER_BOX"])


@app.route("/bookings/", methods=["POST"])
def route_bookings():

    # check if fields exist 
    data = request.get_json()
    """
    if "scanContent" not in data:
        return "Missing data for bons or destinations", 400

    data = data["scanContent"]
    """
    if "bons" not in data or "destination" not in data or "recipients" not in data or "amounts" not in data or "units" not in data:
        print(data)
        return "Missing data", 400 

    # fetch data from request
    bons = data["bons"]
    recipients = data["recipients"]
    amounts = data["amounts"]
    units = data["units"]
    destination = data["destination"]

    dt = datetime.datetime.now()
    date = dt.strftime("%Y-%m-%d")
    dtime = dt.strftime("%H-%M-%S")


    # write to csv file
    file_name = get_filename()
    try :
        with open(file_name, "a") as file:
            for i in range(len(bons)):
                bon = bons[i]
                amount = amounts[i]
                unit = units[i]
                row = [bon, destination, recipients, amount, unit, date, dtime]
                writer = csv.writer(file)
                writer.writerow(row)

        return "OK", 200
    except PermissionError:
        return "File is used!", 400




# run the server (only development!)
if __name__ == "__main__":
    app.run(
        host = app.config["HOST"],
        port = app.config["PORT"],
        debug = app.config["DEBUG"],
        ssl_context = "adhoc"
        )