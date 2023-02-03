#REVERTED (git checkout <commit hash> back to:
# e0cc1abdd7b75cbc7bd375b8f9f6aa1102d987ce on ALPHA branch
# PUBLISHED to CHARLEY

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
        input_type = request.form.get('input_type')
        if input_type == 'username':
            username = request.form.get('username')
            username = username[1:]
            url = f'https://www.googleapis.com/youtube/v3/search?part=id&maxResults=1&q={username}&type=channel&key={config.developer_key}'
            response = requests.get(url)
            dataSearchUser = json.loads(response.text)
            # request above using username, get the channel id
            # from the search json object returned 
            channel_id = dataSearchUser['items'][0]['id']['channelId']
        elif input_type == 'channel_id':
            channel_id = request.form.get('channel_id')
        return redirect(f'/stats/{channel_id}')
    return render_template('index.html')

@app.route('/getjson', methods=['GET', 'POST'])
def getjson():
    if request.method == 'POST':
        channel_id_json= request.form.get('channel_id_json')
        url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,contentDetails&id={channel_id_json}&key={config.developer_key}'
        response = requests.get(url)
        data = json.loads(response.text)
        filename = f"{channel_id_json}.json"
        response = filename(json.dumps(data, indent=4))
        response.headers["Content-Disposition"] = "attachment; filename=" + filename
        response.mimetype = 'application/json'
        return response
    # THIS is NOT right... 
    # it needs to generate json.html 
    # or output.json...
    return render_template('getjson.html')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/stats/<channel_id>")
def stats(channel_id):
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