from core import connect_to_db, Activity, Segment
from pathlib import Path
import pandas as pd
import random
import os

engine, session, Base = connect_to_db('sqlite:///activity_db.sqlite', Path(os.getcwd()) / '..')

activities = session.query(Activity)

activity_count = activities.count()
print(f"There are {activity_count} activities in the database.")

all_activities = activities.all()

rlist = []
while len(rlist) < int(activity_count/10):
    num = random.randint(1, activity_count - 1)
    if num not in rlist:
        rlist.append(num)

print(f'{len(rlist)} activities chosen at random.')

rlist = sorted(rlist)

for act_num in rlist:
    act = all_activities[act_num]

    segments = session.query(Segment).filter(Segment.activity_id == act.strava_id).count()

    print(f'Activity {act.name} ({act.start_date_local.isoformat(" ")}) has {segments} segments.')