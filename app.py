import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import func, desc
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



    
#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return ("<h1>Welcome to the Climate App!</h1> </br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    last_year_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365) 
    #create query for /api/v1.0/precipitation   
    # Perform a query to retrieve the date and precipitation scores

    result = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year_date).order_by(Measurement.date).all()
    session.close()
    # create a dictionary from result
    pricipitation_data = []
    for date, prcp in result:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        pricipitation_data.append(pricipitation_dict)

    return jsonify(pricipitation_data)



    
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    ###create query for stations api
    stations_data = session.query(Station.id,Station.station,Station.name, Station.latitude, Station.longitude,Station.elevation).all()
    session.close()
    print("Server received request for 'Stations' page...")
    return jsonify(stations_data)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    last_year_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    active_station = session.query(Measurement.station, 
                    func.count(Measurement.tobs).label('count')
                    ).group_by(Measurement.station).order_by(desc('count')).all()
    #Design a query to retrieve the last 12 months of temperature observation data (tobs) for the most active station

    active_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last_year_date).filter(Measurement.station == active_station[0][0]).all()
    session.close()                   
    print("Server received request for 'Temperature Observations (tobs)' page...")
    return jsonify(active_tobs)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date
@app.route("/api/v1.0/<start>")
def calc_temps_start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    start_date_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()    
    return jsonify(start_date_temp)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
@app.route('/api/v1.0/<start_date>/<end_date>/')
def calc_temps_start_end(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    start_date_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
    print(f"Calculated temp for start date {start_date} & end date {end_date}")
    return jsonify(start_date_temp)
if __name__ == '__main__':
    app.run(debug=True)

