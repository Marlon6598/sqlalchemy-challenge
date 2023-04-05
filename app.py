# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(autoload_with = engine, reflect = True)

# Save references to each table
base.classes.keys()
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print ("Connecting to home page...")
    return (
        f"This is the home page. Welcome to the home page."
        f"Available Routes:<br/>"
        f"/<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/temperature_observations<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    query12mo = dt.date(2017,8,23) - dt.timedelta(days = 365)
    resultsPrcp = session.query(measurement.date,measurement.prcp).filter(measurement.date >= query12mo).all()
    session.close()
    
    precipitation = []
    for x in resultsPrcp:
        prcpDict = {}
        prcpDict["date"] = x["date"]
        prcpDict["prcp"] = x["prcp"]
        precipitation.append(prcpDict)
    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    resultsSta = session.query(station.station).all()
    session.close()
    y = list(np.ravel(resultsSta))
    session.close()
    return jsonify(y)

@app.route("/api/v1.0/temperature_observations")
def tobs():
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    mostActive = "USC00519281"
    tobs = session.query(measurement.station, measurement.tobs).filter(measurement.station==mostActive).\
           filter(measurement.date >= query_date).all()
    session.close()
    
    tobsList = list(np.ravel(tobs))
    return jsonify(tobsList)

@app.route("/api/v1.0/<start>")
def start(start):
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
              filter(measurement.date >= start).all()
    session.close()

    tobsStartDate = []
    for min, avg, max in results:
        tobsStartDict = {}
        tobsStartDict["TMIN"] = min
        tobsStartDict["TAVG"] = avg
        tobsStartDict["TMAX"] = max
        tobsStartDate.append(tobsStartDict) 
    return jsonify(tobsStartDate)

@app.route("/api/v1.0/<start>/<end>")
def startEnd(start, end):
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
              filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    tobsStartEnd = []
    for min, avg, max in results:
        tobsStartEndDict = {}
        tobsStartEndDict["TMIN"] = min
        tobsStartEndDict["TAVG"] = avg
        tobsStartEndDict["TMAX"] = max
        tobsStartEnd.append(tobsStartEndDict) 
    return jsonify(tobsStartEnd)

if __name__ == "__main__":
        app.run(debug = True)