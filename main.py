from flask import Flask, flash, redirect, render_template, request, jsonify
from flask_bootstrap import Bootstrap
import config
import json
import requests
#from isodate import parse_duration
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__, static_folder='static')
Bootstrap(app)

app.logger.setLevel(logging.DEBUG)

def add_commas(number):
    return '{:,}'.format(number)

@app.route("/", methods=['GET', 'POST'])
def access_forms():
    if request.method == 'POST':
        input_type = request.form.get('input_type')
        if input_type == 'username':
            username = request.form.get('username')
            return process_user(username)
        elif input_type == 'channel_id':
            channel_id = request.form.get('channel_id')
            return process_id(channel_id)
    else:
        return render_template('index.html')

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
        #THIS IS ALWAYS RUN...SO THERE IS A FUNDAMENTAL FLAW SOMEWHERE BEFORE.......
        return render_template('ALWAYS_RESULT_OF_SUBMIT.html', channel_id=channel_id)

#API request function
#if 403 key1, try key2 etc
api_keys = config.developer_keys
def make_api_request(url, keys):
    for key in keys:
        full_url = f'{url}&key={key}'
        response = requests.get(full_url)
        if response.status_code != 403:
            return response
    return None

def process_id(channel_id):
    url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}'
    response = make_api_request(url, api_keys)
    if response is None:
        return render_template('403.html')
    data_search_id = json.loads(response.text)
    if data_search_id['items']:
        channel_id = data_search_id['items'][0]['id']
    else:
        return render_template('id_error.html')
    return redirect(f'/stats/{channel_id}')

def process_user(username):
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={username}&type=channel'
    response = make_api_request(url, api_keys)
    if response is None:
        return render_template('403.html')
    data_search_user = json.loads(response.text)
    if data_search_user['items']:
        channel_id = data_search_user['items'][0]['id']['channelId']
    else:
        return render_template('name_error.html')
    return redirect(f'/stats/{channel_id}')

@app.route("/stats/<channel_id>")
def stats(channel_id):
    logger.debug(f"Running stats function for channel ID: {channel_id}") 
    url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet%2Cstatistics&id={channel_id}&key=AIzaSyAPhsJEvl3MaMFj7OE1EqsArdpueMM2m58'
    response = requests.get(url)
    app.logger.debug("Response from API request: %s", response)
    channel_response = json.loads(response.text)
    if channel_response['items']:
        stats = channel_response
    else:
        return render_template('name_error.html')
    return render_template('stats.html', stats=stats)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)