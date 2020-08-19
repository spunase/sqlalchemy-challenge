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


# Create our session (link) from Python to the DB
session = Session(engine)
    
# Calculate the date 1 year ago from the last data point in the database
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
last_year_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365) 
#create query for /api/v1.0/precipitation   
# Perform a query to retrieve the date and precipitation scores
precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year_date).all()

# Save the query results as a Pandas DataFrame and set the index to the date column

climate_df = pd.DataFrame(precipitation_data)
climate_df = climate_df.set_index('date')
# Sort the dataframe by date
climate_df = climate_df.sort_values(by='date')
##Convert the DataFrame to a dictionary
dict_df = climate_df.to_dict()["prcp"]


###create query for stations api
stations_data = session.query(Station.id,Station.station,Station.name, Station.latitude, Station.longitude,Station.elevation).all()
#3active station
active_station = session.query(Measurement.station, 
                    func.count(Measurement.tobs).label('count')
                    ).group_by(Measurement.station).order_by(desc('count')).all()
#Design a query to retrieve the last 12 months of temperature observation data (tobs) for the most active station
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
active_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last_year_date).filter(Measurement.station == active_station[0][0]).all()                   
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


session.close()
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")
    return jsonify(dict_df)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    return jsonify(stations_data)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'Temperature Observations (tobs)' page...")
    return jsonify(active_tobs)
if __name__ == '__main__':
    app.run(debug=True)

