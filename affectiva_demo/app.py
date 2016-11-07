import os
from flask import Flask, render_template, send_from_directory, redirect, url_for
import json
import requests
import data
from requests.auth import HTTPBasicAuth

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG=True,
)

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import json

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']   
        if email is None:
            return render_template('login.html')
        if not data.userExists(email):
            data.createUser(email)
        response = redirect(url_for('index'))
        response.set_cookie('username', email)
        return response
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    response = redirect(url_for('login'))
    response.set_cookie('username', '')
    return response

@app.route("/")
def index():
    username = request.cookies.get('username')
    if not data.userExists(username):
        return redirect(url_for('login'))
    if username is None:
        return redirect(url_for('login'))
    return render_template('index.html', username=username)

@app.route("/postFaces", methods=["POST"])
def postFaces():
    faces = request.json['faces']
    view_id = request.json['view_id']

    view = data.loadView(view_id)
    view['frames'].append(faces)
    data.saveView(view)

    return "success"

@app.route("/startView", methods=["POST"])
def startView():
    video_id = request.json['video_id']
    view_id = data.createView(video_id)
    return view_id

@app.route("/finishView", methods=["POST"])
def finishView():
    username = request.cookies.get('username')
    view_id = request.json['view_id']
    user = data.loadUser(username)
    user['views'].append(view_id)
    data.saveUser(user)
    return "success"

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    app.run(host='0.0.0.0', port=port)
