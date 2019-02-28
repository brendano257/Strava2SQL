from core import connect_to_db, Activity
import pandas as pd
import os

# A quick demo that loads all rides, and prints out averages by day of the week.

engine, session, Base = connect_to_db('sqlite:///activity_db.sqlite', os.getcwd())

data = session.query(Activity.start_date_local, Activity.name, Activity.distance).filter(Activity.type == 'Ride').all()

df = pd.DataFrame(data)
df['dow'] = df['start_date_local'].dt.dayofweek

dow = df.groupby(['dow']).mean()
dow.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
print(dow)
