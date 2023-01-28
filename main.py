#import os
from flask import Flask, flash, redirect, render_template, request, jsonify
#from random import randint
import config
import json
from googleapiclient.discovery import build
import requests
from isodate import parse_duration

app = Flask(__name__, static_folder='static')

@app.route("/")
def stats_title():

    youtube = build('youtube', 'v3', \
        developerKey=config.developer_key)
    channel_request = youtube.channels().list(
        part='snippet,statistics',
        id=config.channel_id)
    channel_response = channel_request.execute()

    #Note that this needs channelId?
    # Yes, the response needs channel
    # id in order to get most recent
    # video
    #search_request = youtube.search().list(
    #    part='snippet',
    #    channelId=config.channel_id)
    #
    # Trying chat gpt code using
    # import requests instead
    # be careful with the \ ... it breaks code now ok
    url = f'https://www.googleapis.com/youtube/v3/search?key=\
        {config.developer_key}&channelId={config.channel_id}\
            &part=snippet,id&order=date&maxResults=1'
    search_response = requests.get(url).json()
    # Above works...
    #
    # get duration, it first needs the video id of most 
    # recent video....
    #
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={config.channel_id}&maxResults=1&order=date&type=video&key={config.developer_key}'

    response = requests.get(url)
    data = json.loads(response.text)
    video_id = data['items'][0]['id']['videoId']

    url = f'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={video_id}&key={config.developer_key}'
    response = requests.get(url)
    data = json.loads(response.text)
    video_duration = data['items'][0]['contentDetails']['duration']
    # Parse the duration using the parse_duration function
    parsed_duration = parse_duration(video_duration)

    # Extract the hours, minutes, and seconds from the parsed duration
    hours = parsed_duration.seconds // 3600
    minutes = (parsed_duration.seconds % 3600) // 60
    seconds = parsed_duration.seconds % 60

    duration_string = f"{hours} hours, {minutes} minutes, {seconds} seconds"
    
    return render_template('stats.html', \
        channel_resource=channel_response, \
        search_resource=search_response, \
        latest_video_duration=duration_string)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)