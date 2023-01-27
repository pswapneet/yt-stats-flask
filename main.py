import os
from flask import Flask, flash, redirect, render_template, request, jsonify
from random import randint
import config
import json
from googleapiclient.discovery import build

app = Flask(__name__)

@app.route("/")
def dlf_stats():
    youtube = build('youtube', 'v3', developerKey=config.developer_key)
    request = youtube.channels().list(part='snippet', \
        id=config.channel_id)
    response = request.execute()
    return render_template('stats.html', resource=response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)