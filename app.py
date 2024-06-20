from flask import Flask, render_template, request, jsonify
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__, static_folder='templates')

client_id = 'b5ee7d8e74d4436ab2c023cb7a0e9c54'
client_secret = 'dbfc0eef9eda45efa893720e0560b55c'

# Authenticate
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


def get_song_info(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if not results['tracks']['items']:
        return None, None

    track = results['tracks']['items'][0]
    thumbnail_url = track['album']['images'][0]['url'] if track['album']['images'] else 'No image available'
    artist_name = track['artists'][0]['name']
    track_name = track['name']
    song_info = {
        'thumbnail': thumbnail_url,
        'song_name': f"{track_name} by {artist_name}"
    }

    return song_info, thumbnail_url


def get_song_recommendation():
    global current_song
    song_name = current_song.replace('by', '')
    results = sp.search(q=song_name, limit=1, type='track')
    if not results['tracks']['items']:
        return "Song not found"

    track_id = results['tracks']['items'][0]['id']
    recommendations = sp.recommendations(seed_tracks=[track_id], limit=1)
    if not recommendations['tracks']:
        return "No recommendations found"

    recommended_track = recommendations['tracks'][0]
    track_name = recommended_track['name']
    artist_name = recommended_track['artists'][0]['name']

    current_song = f"{track_name} by {artist_name}"

    return current_song


def get_audio_info(query):
    global current_song
    current_song = query
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            search_results = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            audio_url = search_results['url']
            song_info, _ = get_song_info(query)
            if not song_info:
                return None, None, None
            thumbnail_url = song_info['thumbnail']
            song_name = song_info['song_name']
            return audio_url, thumbnail_url, song_name
        except Exception as e:
            print(f"Error fetching audio URL: {e}")
            return None, None, None


@app.route('/play', methods=['GET'])
def play():
    song_name = request.args.get('songName')
    if song_name:
        audio_url, thumbnail_url, song_name = get_audio_info(song_name)
        if audio_url:
            return jsonify({'status': 'success', 'url': audio_url, 'thumbnail': thumbnail_url, 'songName': song_name})
        else:
            return jsonify({'status': 'error', 'message': 'Song not found'}), 404
    else:
        return jsonify({'status': 'error', 'message': 'Song name not provided'}), 400


@app.route('/nextsong', methods=['GET'])
def next_song():
    song_name = get_song_recommendation()
    audio_url, thumbnail_url, song_name = get_audio_info(song_name)
    if audio_url:
        return jsonify({'status': 'success', 'url': audio_url, 'thumbnail': thumbnail_url, 'songName': song_name})
    else:
        return jsonify({'status': 'error', 'message': 'Next song not found'}), 404


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
