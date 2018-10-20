import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

# DB Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect database into model
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#Flask Setup
app = Flask(__name__)

#Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'enterstartdate'<br>"
        f"/api/v1.0/'enterstartdate'/'enterenddate'<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    perc_data = session.query(Measurement.date, Measurement.prcp).all()

    precip = []
    for data in perc_data:
        precip_dict = {}
        precip_dict[data.date] = data.prcp
        precip.append(precip_dict)
    
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    result = session.query(Station.name).all()

    all_stations = list(np.ravel(result))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    max_date = dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.id.desc()).first()[0], '%Y-%m-%d')
    last_year_date = max_date - dt.timedelta(days=366)
    
    # Perform a query to retrieve the data and precipitation scores
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > last_year_date).all()

    tobs = []
    for data in tobs_data:
        tobs_dict = {}
        tobs_dict[data.date] = data.tobs
        tobs.append(tobs_dict)
    
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def tempmorethanstart(start):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start_date).all()
    tobs_dict = {}
    tobs_dict["TMIN"] = results[0][0]
    tobs_dict["TAVG"] = results[0][1]
    tobs_dict["TMAX"] = results[0][2]

    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>/<end>")
def tempmorethanstartend(start, end):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    tobs_dict = {}
    tobs_dict["TMIN"] = results[0][0]
    tobs_dict["TAVG"] = results[0][1]
    tobs_dict["TMAX"] = results[0][2]

    return jsonify(tobs_dict)

if __name__ == '__main__':
    app.run(debug=True)