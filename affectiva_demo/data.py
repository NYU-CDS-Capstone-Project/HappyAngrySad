import json
import requests
from requests.auth import HTTPBasicAuth

base_url = "https://happyangrysad.cloudant.com/"
jsonContentHeaders = {'content-type': 'application/json'}

usersDbAuth = HTTPBasicAuth('dsterentrandellesserywhy', '79ca3b2eba8d9575d50e8ba75c92ec18260bd487')
emotionsDbAuth = HTTPBasicAuth('wonestedidestrowillygeth', 'e635d215e38d37d2847079c1ae4b9584193e24de')

def post(url, data, auth, headers):
	return requests.post(base_url + url, data=json.dumps(data), auth=auth, headers=headers)

def userExists(username):
	query = {
		"selector": {
			"login": {
				"$eq": username
			}
		},
		"fields": [ "login", "views" ]
	}
	r = post('users/_find', query, usersDbAuth, jsonContentHeaders)

	if r.status_code != 200:
		raise Exception("Http error:" + r.text)

	return len(r.json()["docs"]) == 1

def createUser(username):
	doc = {
		'login': username,
		'views': []
	}
	r = post('users', doc, usersDbAuth, jsonContentHeaders)
	if r.status_code != 201:
		raise Exception("Http error:" + r.text)

def saveFaces(id, faces):
	doc = {
		'_id': id,
		'faces': faces
	}
	r = post('emotions', doc, emotionsDbAuth, jsonContentHeaders)
	if r.status_code != 201:
		raise Exception("Http error:" + r.text)
