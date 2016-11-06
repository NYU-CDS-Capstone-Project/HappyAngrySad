import json
import requests
from requests.auth import HTTPBasicAuth

base_url = "https://happyangrysad.cloudant.com/"
jsonContentHeaders = {'content-type': 'application/json'}

usersDbAuth = HTTPBasicAuth('dsterentrandellesserywhy', '79ca3b2eba8d9575d50e8ba75c92ec18260bd487')
emotionsDbAuth = HTTPBasicAuth('wonestedidestrowillygeth', 'e635d215e38d37d2847079c1ae4b9584193e24de')
viewsDbAuth = HTTPBasicAuth('ateryinummothemedenterne', '6e0320b2deac89677bdd580dc48500ad917afc9e')

def post(url, data, auth, headers, expected_code):
	response = requests.post(base_url + url, data=json.dumps(data), auth=auth, headers=headers)
	if response.status_code != expected_code:
		raise Exception("Http error:" + response.text)
	return response

def get(url, auth):
	print("GET URL: " + base_url + url)
	response = requests.get(base_url + url, auth=auth)
	if response.status_code != 200:
		raise Exception("Http error:" + response.text)
	return response

def put(url, data, auth):
	response = requests.put(base_url + url, data=json.dumps(data), auth=auth)
	if response.status_code != 201:
		raise Exception("Http error:" + response.text)	
	print("Response: " + str(response.status_code))

def userExists(username):
	query = {
		"selector": {
			"login": {
				"$eq": username
			}
		},
		"fields": [ "login", "views" ]
	}
	r = post('users/_find', query, usersDbAuth, jsonContentHeaders, 200)
	return len(r.json()["docs"]) == 1

def createUser(username):
	doc = {
		'login': username,
		'views': []
	}
	post('users', doc, usersDbAuth, jsonContentHeaders, 201)

def createView(video_id):
	doc = {
		'video': video_id,
		'frames': []
	}
	r = post('views', doc, viewsDbAuth, jsonContentHeaders, 201)
	id = r.json()['id']
	if (id is None or len(id) == 0):
		raise Exception("Failed to create new view")
	return id

def loadView(id):
	r = get("views/" + id, viewsDbAuth)
	print(r.json())
	return r.json()

def saveView(view):
	put("views/" + view['_id'], view, viewsDbAuth)

def loadUser(username):
	query = {
		"selector": {
			"login": {
				"$eq": username
			}
		},
		"fields": [ "login", "views", "_id", "_rev" ]
	}
	r = post('users/_find', query, usersDbAuth, jsonContentHeaders, 200)
	if (len(r.json()["docs"]) != 1):
		raise Exception("Error loading user '" + username + "'")
	return r.json()["docs"][0]

def saveUser(user):
	put("users/" + user['_id'], user, usersDbAuth)