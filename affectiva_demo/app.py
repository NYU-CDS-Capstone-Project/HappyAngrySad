import os
from flask import Flask, render_template, send_from_directory
import json
import requests
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

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/postFaces", methods=["POST"])
def postFaces():
    print("Will attempt to read 'json'")

    faces = request.json['faces']
    id = request.json['id']
    print(faces)

    doc = {
        '_id': id,
        'faces': faces
    }

    auth=HTTPBasicAuth('wonestedidestrowillygeth', 'e635d215e38d37d2847079c1ae4b9584193e24de')
    headers = {'content-type': 'application/json'}
    r = requests.post('https://happyangrysad.cloudant.com/emotions', data=json.dumps(doc), auth=auth, headers=headers)
    print r
    print r.text

    return "postFaces succeeded!"

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))

    app.run(host='0.0.0.0', port=port)