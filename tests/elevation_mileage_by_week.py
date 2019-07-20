from core import connect_to_db, Activity
import matplotlib.pyplot as plt
import datetime as dt
from datetime import datetime
import pandas as pd
import os

engine, session, Base = connect_to_db('sqlite:///activity_db.sqlite', os.getcwd())

activities = (session.query(Activity)
                     .filter(Activity.type == 'Run')
                     .filter(Activity.start_date > datetime(2019, 4, 1)))

weeks = pd.date_range(datetime(2019, 4, 1), datetime(2019, 7, 15), freq='7d')

weeks_elevation = {}
weeks_mileage = {}

for week in weeks:
    elev = 0
    mileage = 0

    acts_select = activities.filter(Activity.start_date >= week,
                                    Activity.start_date < week + dt.timedelta(days=7)).all()

    for act in acts_select:
        elev += act.total_elevation_gain * 3.281  # convert to feet from meters
        mileage += act.distance / 1609  # convert to miles from meters

    weeks_elevation[week] = elev
    weeks_mileage[week] = mileage


from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

f1 = plt.figure()
ax = f1.gca()
ax2 = ax.twinx()

ax.plot(list(weeks_elevation.keys()), list(weeks_elevation.values()), '-og')
ax2.plot(list(weeks_mileage.keys()), list(weeks_mileage.values()), '-or')

ax.tick_params(axis='both', which='major', size=8, width=2, labelsize=15)
ax.tick_params(axis='x', labelrotation=20)
[i.set_linewidth(2) for i in ax.spines.values()]
f1.set_size_inches(11.11, 7.406)
f1.subplots_adjust(bottom=.10)

ax.set_ylabel('Elevation (ft)', fontsize=20)
ax2.set_ylabel('Distance (miles)', fontsize=20)

ax.set_title(f'Elevation and Distance by Week')
ax.legend(['Elevation (ft)'], loc='upper right')
ax2.legend(['Distance (miles)'], loc='upper left')

f1.savefig(f'weekly_distance_elevation.png', dpi=150)
