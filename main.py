#import os
from flask import Flask, flash, redirect, render_template, request, jsonify
from flask_bootstrap import Bootstrap
import config
import json
from googleapiclient.discovery import build
import requests
from isodate import parse_duration
#import urllib.parse
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import DataRequired

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = '1234asdf'
Bootstrap(app)

def add_commas(number):
    return '{:,}'.format(number)

class searchForm(FlaskForm):
    input_type = RadioField('Input Type', choices=[('username', 'Username'), ('id', 'ID')], validators=[DataRequired()])
    input_value = StringField('Input Value', validators=[DataRequired()])


#oldforms

@app.route("/", methods=['GET', 'POST'])
def access_forms():
    if request.method == 'POST':
        input_type = request.form.get('input_type')
        if input_type == 'username':
            username = request.form.get('username')
            process_user(username)
        elif input_type == 'channel_id':
            channel_id = request.form.get('channel_id')
            process_id(channel_id)
    else:
        return render_template('index.html')
#THE v3/search with key b8 error 403... maybe that why it didnt work.... push and revert to old shit
#new form

@app.route("/getjson", methods=['GET', 'POST'])
def input_form():
    form = searchForm()
    if form.validate_on_submit():
        input_type = form.input_type.data
        input_value = form.input_value.data
        if input_type == 'id':
            wtfurl = f'https://www.googleapis.com/youtube/v3/search?part=id&channelId={input_value}&key={config.developer_key}'
            wtfresponse = requests.get(wtfurl)
            wtfdata = json.loads(wtfresponse)
            return render_template('json.html', wtf=wtfdata)
        #    process_id(input_value)
        elif input_type == 'username':
             process_user(input_value)
        #    #JUST BUILD IN THE JSON SHIT HERE MAYBE IDK GOTTA CHECK THE JSON BS RESPONSE NPONSENSE BSSSSSSSS FUCKCKCCCDG
    return render_template('getjson.html', form=form)

def process_id(channel_id):
    url = f'https://www.googleapis.com/youtube/v3/search?part=id&channelId={channel_id}&key={config.developer_key}'
    response = requests.get(url)
    #convert to python list or whatever why .text ????
    data_search_id = json.loads(response.text)
    if data_search_id['items']:
        channel_id = data_search_id['items'][0]['id']['channelId']    
    else:
        return render_template('id_error.html')
    return redirect(f'/stats/{channel_id}')

def process_user(username):
    url = f'https://www.googleapis.com/youtube/v3/search?part=id&maxResults=1&q={username}&type=channel&key={config.developer_key}'
    response = requests.get(url)
    data_search_user = json.loads(response.text)
    if data_search_user['items']:
        channel_id = data_search_user['items'][0]['id']['channelId']
    else:
        return render_template('name_error.html')
    return redirect(f'/stats/{channel_id}')

@app.route("/stats/<channel_id>")
def stats(channel_id):
    youtube = build('youtube', 'v3', developerKey=config.developer_key)
    channel_request = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id)
    channel_response = channel_request.execute()
    statsChannel = channel_response

    #add commas to some stats

    #views
    totalviews = int(statsChannel["items"][0]["statistics"]["viewCount"])
    views_string = str(totalviews)
    if len(views_string) >= 3:
        views_string = (add_commas(totalviews))

    #subs
    totalsubs = int(statsChannel["items"][0]["statistics"]["subscriberCount"])
    subs_string = str(totalsubs)
    if len(subs_string) >= 3:
        subs_string = (add_commas(totalsubs))

    #videos
    total_videos = int(statsChannel["items"][0]["statistics"]["videoCount"])
    video_string = str(total_videos)
    if len(video_string) >= 3:
        video_string = (add_commas(total_videos))

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
        totalsubs=subs_string,
        totalviews=views_string,
        totalvideos=video_string)

@app.route("/stats/<channel_id>", methods=['GET', 'POST'])
def access_forms_on_stats_page(channel_id):
    if request.method == 'POST':
        input_type = request.form.get('input_type')
        if input_type == 'username':
            username = request.form.get('username')
            return process_user(username)
        elif input_type == 'channel_id':
            channel_id = request.form.get('channel_id')
            return process_id(channel_id)
    else:
        return render_template('stats.html', channel_id=channel_id)

#work in progress below

def getjsonold():
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
    app.run(host='0.0.0.0', port=5000, debug=False)