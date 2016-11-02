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
        if data.userExists(email):
            print("User " + email + " exists! Redirecting to home page")
        else:
            print("User " + email + " doesn't exist, will create")
            data.createUser(email)

        response = redirect(url_for('index'))
        response.set_cookie('username', email)
        return response

    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    response = redirect(url_for('login'))
    response.set_cookie('username', 'OLOLO')
    return response

@app.route("/")
def index():
    # Do we have the auth cookie? 
    username = request.cookies.get('username')
    if not data.userExists(username):
        return redirect(url_for('login'))
    if username is None:
        print("Auth cookie not set, redirecting to login page")
        return redirect(url_for('login'))
    print("Auth cookie it set, login=" + username)
    return render_template('index.html', username=username)

@app.route("/postFaces", methods=["POST"])
def postFaces():
    faces = request.json['faces']
    id = request.json['id']
    data.saveFaces(id, faces)
    return "postFaces succeeded!"

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))

    app.run(host='0.0.0.0', port=port)