# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import flask
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine, reflect = True)

# Save references to each table
Base.classes.keys()
measurement = Base.classes.measurement
station = Base.classes.station

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
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation:<br/>"
        f"api/v1.0/stations:<br/>"
        f"/api/v1.0/tobs:<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(measurement.prcp).all()
    session.close()
    
    precipitation = []
    for x in results:
        prp_dict = {}
        prp_dict[x[0]] = x[1]
        precipitation.append(prp_dict)
    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    station = session.query(station.station).all()
    
    d = {k[0]:'' for k in station}
    session.close()
    
    return jsonify(d)

@app.route("/api/v1.0/tobs")
def most_active():
    session = Session(engine)
    most_active = session.query(measurement.station, func.count(measurement.station)).\
              group_by(measurement.station).\
              order_by(func.count(measurement.station).desc()).all()
    print(most_active)
    session.close()

    most_active_station = most_active[0][0]
    
    temps_last_year = session.query(measurement.tobs).\
                      filter(measurement.station == most_active_station).\
                      filter(measurement.date >= '2016-08-23').all()

    temps_list = list(np.ravel(temps_last_year))
    return jsonify(temps_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def min_max_avg(start, end = None):
    session = Session(engine)
    if end:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                  filter(measurement.date >= start).filter(measurement.date <= end).all()
    else:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                  filter(measurement.date >= start).all()

    session.close()

    all_temps = []
    for min_temp, avg_temp, max_temp in results:
        temp_dict = {}
        temp_dict['min_temp'] = min_temp
        temp_dict['avg_temp'] = avg_temp
        temp_dict['max_temp'] = max_temp
        all_temps.append(temp_dict)

    return jsonify(all_temps)

if __name__ == "__main__":
    app.run(debug = True)