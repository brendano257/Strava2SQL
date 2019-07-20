import time
import datetime as dt
import os
import json
import requests

from core import Activity, Segment, Athlete, connect_to_db

engine, session, Base = connect_to_db('sqlite:///activity_db.sqlite', os.getcwd())

Base.metadata.create_all(engine)

with open('client_data.txt', 'r') as file:
    client_data = json.loads(file.read())

refresh_base = 'https://www.strava.com/oauth/token'
refresh_data = ({'client_id': client_data['client_id'], 'client_secret': client_data['client_secret'],
                 'refresh_token': client_data['refresh_token'], 'grant_type': 'refresh_token'})

response = requests.post(refresh_base, data=refresh_data)

client_data['access_token'] = response.json().get('access_token')
client_data['refresh_token'] = response.json().get('refresh_token')

token = f'Bearer {client_data["access_token"]}'
athlete_base = "https://www.strava.com/api/v3/athlete/activities"

ct = 0
act_list = []
for page in range(1, 10000):  # edit page number to be at least > your_activity_count / 50
    athlete_header = {'Authorization': token}
    athlete_params = {'page': page, 'per_page': '50'}

    athlete_ret = requests.get(athlete_base, headers=athlete_header, params=athlete_params).json()

    if len(athlete_ret) is 0:
        print(f'No more data found after page {page}. {len(act_list)} activities were retrieved.')
        break

    activities = [act for act in athlete_ret]

    for act in activities:
        act_list.append(Activity(act))

    for act in act_list:
        session.add(act)
    session.commit()  # commit after every page

    ct += 1

activity_ids = [a[0] for a in session.query(Activity.strava_id).all()]
# unpack result tuples to get ids of all activities to request segments for

segment_list = []
for strava_id in activity_ids:

    if ct == 575:
        print('Sleeping 15 minutes to out-wait Strava API limit for basic applications.')
        print(f'Will resume at {(dt.datetime.now() + dt.timedelta(minutes=15, seconds=15)).isoformat(" ")}')
        time.sleep(60 * 15 + 15)  # if at 575 requests, sleep for ~15 minutes to out-wait strava default API limit

    activity_base = f"https://www.strava.com/api/v3/activities/{strava_id}"
    activity_header = {'Authorization': token}
    activity_params = {'include_all_efforts': 'True'}

    activity_response = requests.get(activity_base, headers=activity_header, params=activity_params).json()

    segment_efforts = activity_response.get('segment_efforts')

    if len(segment_efforts) > 0:
        for segment in segment_efforts:
            segment_list.append(Segment(segment))

    for seg in segment_list:
        session.add(seg)
    session.commit()

    ct += 1