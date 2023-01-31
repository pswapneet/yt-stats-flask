#FLASK APP with problems...
#"The issue was that the request object from the 
# flask library was being overwritten by 
# the request object from the youtube API.
from flask import Flask, flash, redirect, render_template, request, jsonify

#STORE THE API KEY
import config

#YOUTUBE CLIENT API
from googleapiclient.discovery import build

#ALPHA release, working with both YT CLIENT API above and requests/json
import requests
import json

#USED FOR PARSING video_duration
from isodate import parse_duration

# APP BELOW

#THE CSS IS in /static/css
app = Flask(__name__, static_folder='static')

#VARIABLE FOR THE YouTube Client API!
youtube = build('youtube', 'v3', developerKey=config.developer_key)

# index.html

@app.route("/", methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        channel_input = request.form.get('channel_input')
        input_type = request.form.get('input_type')
        if input_type == 'channel_id':
            channel_id = channel_input
        elif input_type == 'username':
            username = channel_input[1:]
            url = f'https://www.googleapis.com/youtube/v3/channels?part=forUsername={username}&key={config.developer_key}'
            response = requests.get(url)
            data = json.loads(response.text)
            usernamereq= data
            return render_template('test.html', test1=usernamereq)
        elif input_type == 'custom_url':
            url = f'https://www.googleapis.com/youtube/v3/channels?part=id&url={channel_input}&key={config.developer_key}'
            response = requests.get(url)
            data = json.loads(response.text)
            channel_id = data['items'][0]['id']
        return redirect(f'/stats/{channel_id}')
    return render_template('index.html')

# getjson.html

@app.route('/getjson', methods=['GET', 'POST'])
def getjson():
    if request.method == 'POST':
        getjson_id = request.form['channel_id']
        youtube = build("youtube", "v3", developerKey=config.developer_key)
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics,topicDetails",
            id=getjson_id)
        response = request.execute()
        return render_template('json.html', data=response)
    return render_template('getjson.html')

# about.html

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/stats/<channel_id>")
def stats(channel_id):
    #youtube = build('youtube', 'v3', developerKey=config.developer_key)
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

#RUN THE APP BELOW

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)