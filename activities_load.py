import os, json, requests

from core import Activity, connect_to_db

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
session.commit()