import data
import os
from flask import Flask, render_template, redirect, url_for
import time
import json
import requests
import random
import threading
from requests.auth import HTTPBasicAuth
import model as m


# initialization
app = Flask(__name__)

from datetime import timedelta
from flask import request
import json
import sys
import getopt


default_recommendations = ["EFpwgXCwMNQ", "3ZqPaohVjmw", "_OBlgSz8sSM",
                           "sJgDYdA8dio", "Fc1P-AEaEp8", "7QLSRMoKKS0",
                           "a1Y73sPHKxw"]


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


@app.route('/webcamDisplay', methods=['GET'])
def webcamDisplay():
    '''
    Purpose:
        redirect method to send user back to webcam visualization page
    Parameters:
        n/a
    Returns:
        response with URL redirect and cleared cookie value for username
    '''
    #response = redirect(url_for('webcamDisplay'))
    return render_template('webcamDisplay.html')


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
        string indicating success
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
    # post graph edge of user view
    data.updateGraph(view_id, user['_id'])
    # updates user record with view_id
    user['views'].append(view_id)
    # marks user as dirty so model scripts know to update recommendations
    user['dirty'] = True
    # saves updated user record
    data.saveUser(user)
    return "success"


@app.route("/getRecommendations", methods=["GET"])
def getRecommendations():
    username = request.cookies.get('username')
    user = data.loadUser(username)
    recommendations = default_recommendations[0:6]
    if 'recommendations' in user and type(user['recommendations']) == list:
        if len(user['recommendations']) >= 6:
            recommendations = user['recommendations']
        else:
            numRecomsToUse = 6 - len(user['recommendations'])
            recommendations = user['recommendations'] + \
                recommendations[:numRecomsToUse]
    return json.dumps(recommendations)


def recomputeRecommendations():
    print("Summary Stats - Will wait for the server to start")
    time.sleep(5)  # Let the server start first
    print("recomputeRecommendations thread started")
    while True:
        time.sleep(2)
        users = data.getDirtyUsers()
        print 'users'
        print users
        if (len(users) == 0):
            time.sleep(1)
            continue

        print("There are " + str(len(users)) + " dirty users")
        user_id = users[0]["_id"]
        login = users[0]["login"]
        print("Will recompute recommendations for user '" + login + "'")
        print("Will recompute recommendations for user '" + user_id + "'")
        recommendations = m.getBestRec(user_id)
        print type(recommendations)

        user = data.loadUser(login)
        user["recommendations"] = recommendations
        user["dirty"] = False
        data.saveUser(user)
        print("Done with recommendations for user '" + login + "'")


def main(args):
    if args == ['--env=prod']:
        print("Running in production mode!")
        data.env = 'prod'
    else:
        print("Running in test mode")

    port = int(os.environ.get("PORT", 8080))

    recommendationsThread = threading.Thread(target=recomputeRecommendations)
    recommendationsThread.daemon = True
    recommendationsThread.start()
    app.run(host='0.0.0.0', port=port, threaded=True)

# launch
if __name__ == "__main__":
    main(sys.argv[1:])
