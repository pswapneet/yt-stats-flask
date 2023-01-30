#import os
from flask import Flask, flash, redirect, render_template, request, jsonify
#from random import randint
import config
import json
from googleapiclient.discovery import build
import requests
from isodate import parse_duration

app = Flask(__name__, static_folder='static')

#working on alpha...
# going to add a form 
# for input channel_id
#import os
from flask import Flask, flash, redirect, render_template, request, jsonify
import config
import json
from googleapiclient.discovery import build
import requests
from isodate import parse_duration

app = Flask(__name__, static_folder='static')

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        channel_id = request.form.get('channel_id')
        return redirect(f'/stats/{channel_id}')
    return render_template('index.html')

@app.route("/stats/<channel_id>")
def stats_title(channel_id):
    youtube = build('youtube', 'v3', developerKey=config.developer_key)
    channel_request = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id)
    channel_response = channel_request.execute()

    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=1&order=date&type=video&key={config.developer_key}'
    response = requests.get(url)
    search_response = json.loads(response.text)
    video_id = search_response['items'][0]['id']['videoId']

    url = f'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={video_id}&key={config.developer_key}'
    response = requests.get(url)
    data = json.loads(response.text)
    video_duration = data['items'][0]['contentDetails']['duration']
    parsed_duration = parse_duration(video_duration)

    hours = parsed_duration.seconds // 3600
    minutes = (parsed_duration.seconds % 3600) // 60
    seconds = parsed_duration.seconds % 60

    duration_string = f"{hours} hours, {minutes} minutes, {seconds} seconds"

    return render_template('stats.html', \
        channel_resource=channel_response, \
        latest_video_duration=duration_string, \
        search_resource=search_response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)