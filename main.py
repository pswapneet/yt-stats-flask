#import os
from flask import Flask, flash, redirect, render_template, request, jsonify
import config
import json
from googleapiclient.discovery import build
import requests
from isodate import parse_duration

app = Flask(__name__, static_folder='static')

def add_commas(number):
    return '{:,}'.format(number)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        #username or channel_id form
        input_type = request.form.get('input_type')

        #username input
        if input_type == 'username':
            username = request.form.get('username')
            username = username[1:]
            url = f'https://www.googleapis.com/youtube/v3/search?part=id&maxResults=1&q={username}\
                &type=channel&key={config.developer_key}'
            response = requests.get(url)
            dataSearchUser = json.loads(response.text)

            #Check if username response is OK 
            #i.e. items is NOT empty
            if dataSearchUser['items']:
                channel_id = dataSearchUser['items'][0]['id']['channelId']
            #items is empty
            else:
                return render_template('name_error.html')
        
        #channel_id input
        elif input_type == 'channel_id':
            channel_id = request.form.get('channel_id')
            url = f'https://www.googleapis.com/youtube/v3/search?part=id&channelId={channel_id}\
                &key={config.developer_key}'
            response = requests.get(url)
            dataSearchID = json.loads(response.text)

            #check items
            if dataSearchID['items']:
                channel_id = dataSearchID['items'][0]['id']['channelId']    
            else:
                return render_template('id_error.html')

        #variable channel_id passed to stats         
        return redirect(f'/stats/{channel_id}')

    return render_template('index.html')

@app.route("/stats/<channel_id>")
def stats(channel_id):

    #get some stats with the youtube python client library
    youtube = build('youtube', 'v3', developerKey=config.developer_key)
    channel_request = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id)
    channel_response = channel_request.execute()
    statsChannel = channel_response

    totalviews = int(statsChannel["items"][0]["statistics"]["viewCount"])
    
    views_string = str(totalviews)
    if len(views_string) >= 3:
        #the number gets backwards...
        views_string_bs = ",".join([views_string[max(0, i-3):i] for i in range(len(views_string), 0, -3)])[::-1]
        views_string = (add_commas(totalviews))

    #get the video id which is used in next api req
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&\
        maxResults=1&order=date&type=video&key={config.developer_key}'
    response = requests.get(url)
    search_response = json.loads(response.text)
    video_id = search_response['items'][0]['id']['videoId']

    #video_id from search_response (latest video)
    url = f'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={video_id}&key={config.developer_key}'
    response = requests.get(url)
    dataLatest = json.loads(response.text)

    #format duration latest video
    video_duration = dataLatest['items'][0]['contentDetails']['duration']
    parsed_duration = parse_duration(video_duration)
    hours = parsed_duration.seconds // 3600
    minutes = (parsed_duration.seconds % 3600) // 60
    seconds = parsed_duration.seconds % 60

    duration_string = f"{hours} hours, {minutes} minutes, {seconds} seconds"

    return render_template('stats.html', \
        channel_resource=channel_response, \
        latest_video_duration=duration_string, \
        search_resource=search_response, \
        totalviewsbs=views_string_bs,
        totalviews=views_string)
        
@app.route('/getjson', methods=['GET', 'POST'])

#work in progress below
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
    return render_template('getjson.html')

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)