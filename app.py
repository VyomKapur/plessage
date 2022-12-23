from os import access
from flask import Flask, redirect, url_for, render_template, request, flash
from urllib.parse import urlencode

from requests import session

from spotify import spotify
client_obj = spotify.SpotifyAPI()

app = Flask(__name__)

session = {}

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/auth', methods=['POST', 'GET'])
def auth():
    url = client_obj.perform_auth()
    return redirect(url)

@app.route('/callback', methods=['POST', 'GET'])
def callback():
    auth_token = request.args['code']
    res = client_obj.get_access_token(auth_token)
    session_access_token = res['access_token']
    session['access_token'] = session_access_token
    return login_sucess()

@app.route('/login_sucess', methods=['POST', 'GET'])
def login_sucess():
    return render_template('index.html')

@app.route('/computation', methods=['POST', 'GET'])
def computation():
    if request.method == "POST":
        message = request.form.get("message")
    access_token = session['access_token']
    res = client_obj.get_user_id(access_token)
    id = res['id']
    playlist_id = client_obj.create_session_playlist(message, id, access_token)
    print(playlist_id)
    uris, track_ids = client_obj.get_required_songs(message, access_token)
    res = client_obj.add_to_playlist(playlist_id, uris, access_token)
    session['track_id'] = track_ids
    return redirect(url_for('result'))

@app.route('/result')
def result():
    track_id = session['track_id']
    return render_template('result.html', track_id = track_id)

if __name__ == "__main__":
    app.run(debug=True)