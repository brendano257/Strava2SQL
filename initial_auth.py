import webbrowser
import requests
import json
from requests import Session, Request

# Client ID and Secret and can found at https://www.strava.com/settings/api once you have registered your application
# with Strava.

c_id = input('What is your Strava client ID? ')
c_secret = input('What is your Strava client secret? ')

client_data = {'client_id': c_id, 'client_secret': c_secret}

base = "https://www.strava.com/oauth/authorize"

scopes = 'read,read_all,activity:read,activity:read_all'  # edit this to add any scopes you want/need w/ your token

header = ({'client_id': client_data['client_id'], 'response_type': 'code', 'redirect_uri': 'http://localhost/exchange_token',
          'approval_prompt': 'force', 'scope': scopes})

s = Session()
p = Request('GET', base, params=header).prepare()

webbrowser.open(p.url)

print("'localhost' will refuse to connect. In the URL, there will be code=xxxxxx&... Copy the x's below.")
code = input('What was the authorization code embedded in the URL?')

postdata = {'client_id': client_data['client_id'], 'client_secret': client_data['client_secret'], 'code': code, 'grant_type': 'authorization_code'}

token_base = "https://www.strava.com/oauth/token"

auth_return = requests.post(token_base, data=postdata).json()

client_data['access_token'] = auth_return.get('access_token')
client_data['refresh_token'] = auth_return.get('refresh_token')

with open('client_data.txt', 'w') as file:
    file.write(json.dumps(client_data))

print(f"Your access token is {client_data['access_token']} and has been saved to client_data.txt")




