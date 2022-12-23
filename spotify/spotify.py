import requests, json
import base64
import datetime
from urllib.parse import urlencode



class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expires = True
    client_id = "YOUR CLIENT ID"
    client_secret = "YOUR CLIENT SECRET"
    token_url = "https://accounts.spotify.com/api/token"
    method = "POST"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_client_credentials(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None or client_secret == None:
            raise Exception("Enter not None client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
    
    def get_token_header(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        } 

    def get_token_data(self):
        return {
            'grant_type': 'client_credentials'
        }

    def perform_auth(self):
        query_params = {
            'client_id': "CLIENT ID",
            'response_type': 'code',
            'redirect_uri': 'http://127.0.0.1:5000/callback',
            'scope': "user-library-read playlist-modify-public",
            'show_dialog': 'true'
        }
        url = "https://accounts.spotify.com/authorize/"
        url = f"{url}?{urlencode(query_params)}"
        return url

    def get_access_token(self, req_code):
        client_id = self.client_id
        client_secret = self.client_secret
        url =  'https://accounts.spotify.com/api/token'
        token_data = { 
            'code':  req_code,
            'redirect_uri': 'http://127.0.0.1:5000/callback',
            'grant_type': 'authorization_code'
        }
        headers = self.get_token_header()

        r = requests.post(url, data=token_data, headers=headers)
        return r.json()

    def get_user_id(self, user_access_token):
        profile_url = 'https://api.spotify.com/v1/me'
        Authorization = {
            'Authorization': f"Bearer {user_access_token}"
        }
        r = requests.get(profile_url, headers=Authorization)
        return r.json()

    def create_session_playlist(self, message, id, access_token):
        playlist_url = f"https://api.spotify.com/v1/users/{id}/playlists"
        print(playlist_url)
        headers = {
            "Content-Type":"application/json", 
            'Authorization': f'Bearer {access_token}'
        }
        body =  json.dumps({
            'name': f"{message}",
            'description': "New playlist description",
            'public': True
        })
        r = requests.post(url=playlist_url,data=body, headers=headers)
        print(r.json())
        return r.json()['id']

    def search(self, song, access_token):
        search_url = "https://api.spotify.com/v1/search"
        offset = 0
        found = False
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        body =  urlencode({
            'q': f"{song}",
            'type': 'track',
            'limit': '50',
            'offset': f"{offset}"
        })
        lookup = f"{search_url}?{body}"
        r = requests.get(lookup, headers=headers)
        worst_case = r.json()['tracks']['items'][0]['id']
        while found==False and offset <=1000:
            body =  urlencode({
                'q': f"{song}",
                'type': 'track',
                'limit': '50',
                'offset': f"{offset}"
            })
            lookup = f"{search_url}?{body}"
            r = requests.get(lookup, headers=headers)
            try:
                for i in range(len(r.json()['tracks']['items'])):
                    if r.json()['tracks']['items'][i]['name'] == f"{song}":
                        print("yes")
                        return r.json()['tracks']['items'][i]['id']
                    else:
                        print('no')
                offset += 50
            except:
                return worst_case
        return worst_case

    def uri(self, id, access_token):
        search_url = "https://api.spotify.com/v1/tracks/"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        lookup = f"{search_url}{id}"
        r = requests.get(lookup, headers=headers)
        print(r.json()['uri'])
        return r.json()['uri']

    def get_required_songs(self, message, access_token):
        songs = message.split()
        uris = []
        ids = []
        for song in songs:
            id = self.search(song, access_token)
            ids.append(id)
            uris.append(self.uri(id, access_token))
        print(uris)
        return uris, ids
    
    def add_to_playlist(self, playlist_id, uris, access_token):
        endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        request_body = json.dumps({
            "uris" : uris
        })
        r = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", "Authorization":f"Bearer {access_token}"})
        print(r.json())
        return None

