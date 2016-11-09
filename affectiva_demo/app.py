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
    '''
    Purpose:
        Handles user email input, checks whether they exist, creates
        new one if needed, and finally sends them to index.html
    Parameters:
        N/A
    Returns:
        index.html template
    '''
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
    '''
    Purpose:
        redirect method to send user back to login page
    Parameters:
        n/a
    Returns:
        response with URL redirect and cleared cookie value for username
    '''
    response = redirect(url_for('login'))
    response.set_cookie('username', '')
    return response


@app.route("/")
def index():
    '''
    Purpose:
        Checks if user is signed-in, redircts to login page if not,
        and serves serve the index.html if they are signed-in.
    Parameters:
        N/A
    Returns:
        index.html template
    '''
    username = request.cookies.get('username')
    if not data.userExists(username):
        return redirect(url_for('login'))
    if username is None:
        return redirect(url_for('login'))
    return render_template('index.html', username=username)


@app.route("/postFaces", methods=["POST"])
def postFaces():
    '''
    Purpose:
        Receives data from the AJAX call that includes
        user and view data, which is then posted to the DB.
    Parameters:
        N/A
    Returns:
        string idicating success
    '''
    # get the data from the dictionary sent by AJAX call.
    faces = request.json['faces']
    view_id = request.json['view_id']

    # load the view data from the DB
    view = data.loadView(view_id)
    # append new views to existing
    view['frames'].append(faces)
    # save updated view list to DB
    data.saveView(view)

    return "success"


@app.route("/startView", methods=["POST"])
def startView():
    '''
    Purpose:
        This is initiated at the beginning of a view session
        for one video. It receives data from the AJAX call that includes
        video data, which is then posted to the DB.
    Parameters:
        N/A
    Returns:
        view_id: string containing the id of the view just created
    '''
    # data sent by the AJAX call
    video_id = request.json['video_id']
    # creates the view record in the DB
    view_id = data.createView(video_id)
    return view_id


@app.route("/finishView", methods=["POST"])
def finishView():
    '''
    Purpose:
        Updates the user record to insert the new view record id
        created by watching the previous video.
    Parameters:
        N/A
    Returns:
        succes string to indicate the user record has been updated with the
        newly created view record id.
    '''
    # gets the username from the cookies
    username = request.cookies.get('username')
    # gets the view_id from the AJAX call
    view_id = request.json['view_id']
    # gets the user record from DB
    user = data.loadUser(username)
    # updates user record with view_id
    user['views'].append(view_id)
    # saves updated user record
    data.saveUser(user)
    return "success"

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    app.run(host='0.0.0.0', port=port)
