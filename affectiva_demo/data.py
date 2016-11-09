import json
import requests
from requests.auth import HTTPBasicAuth

base_url = "https://happyangrysad.cloudant.com/"
jsonContentHeaders = {'content-type': 'application/json'}

usersDbAuth = HTTPBasicAuth(
    'dsterentrandellesserywhy', '79ca3b2eba8d9575d50e8ba75c92ec18260bd487')
emotionsDbAuth = HTTPBasicAuth(
    'wonestedidestrowillygeth', 'e635d215e38d37d2847079c1ae4b9584193e24de')
viewsDbAuth = HTTPBasicAuth(
    'ateryinummothemedenterne', '6e0320b2deac89677bdd580dc48500ad917afc9e')


def post(url, data, auth, headers, expected_code):
    '''
    Purpose:
        Generic function for creating "POST" URL strings to interact with DB.
    Parameters:
        url: this indicates the specific Cloudant DB to access
        data: defines how you interact with the DB API
        auth: these are the usernames and keys to the DB
        headers: determines the format of the response
        expected_code: this is the expected response from the DB API
    Returns:
        The response from the DB API
    '''
    response = requests.post(
        base_url + url, data=json.dumps(data), auth=auth, headers=headers)
    if response.status_code != expected_code:
        raise Exception("Http error:" + response.text)
    return response


def get(url, auth):
    '''
    Purpose:
        Generic function for creating "GET" URL strings to interact with DB.
    Parameters:
        url: this indicates the specific DB to access and the data to get.
        auth: these are the usernames and keys to the DB
    Returns:
        The DB API response containing data
    '''
    print("GET URL: " + base_url + url)
    response = requests.get(base_url + url, auth=auth)
    if response.status_code != 200:
        raise Exception("Http error:" + response.text)
    return response


def put(url, data, auth):
    '''
    Purpose:
        Generic function for creating "PUT" URL strings to save data to DB.
    Parameters:
        url: indicates the specific DB to access and the data create/update
        data: specific data to be created/updated in DB.
        auth: these are the usernames and keys to the DB
    Returns:
        N/A
    '''
    response = requests.put(base_url + url, data=json.dumps(data), auth=auth)
    if response.status_code != 201:
        raise Exception("Http error:" + response.text)
    print("Response: " + str(response.status_code))


def userExists(username):
    '''
    Purpose:
        Build url to check DB if User exists
    Parameters:
        username: string entered by user via login page.
    Returns:
        Boolean
    '''
    query = {
        "selector": {
            "login": {
                "$eq": username
            }
        },
        "fields": ["login", "views"]
    }
    r = post('users/_find', query, usersDbAuth, jsonContentHeaders, 200)
    return len(r.json()["docs"]) == 1


def createUser(username):
    '''
    Purpose:
        Creates the URL string to create user in DB
    Parameters:
        username: string input by user on /login page
    Returns:
        N/A
    '''
    doc = {
        'login': username,
        'views': []
    }
    post('users', doc, usersDbAuth, jsonContentHeaders, 201)


def createView(video_id):
    '''
    Purpose:
        Creates the URL string to create View in DB
    Parameters:
        username: string input by user on /login page
    Returns:
        N/A
    '''
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
    '''
    Purpose:
        Get the view from DB based upon a given view_id value
    Parameters:
        id: id of view
    Returns:
        json view record
    '''
    r = get("views/" + id, viewsDbAuth)
    print(r.json())
    return r.json()


def saveView(view):
    '''
    Purpose:
        update the view DB with edited view record
    Parameters:
        id: id of view
    Returns:
        n/a
    '''
    put("views/" + view['_id'], view, viewsDbAuth)


def loadUser(username):
    '''
    Purpose:
        Retrieves from the DB the user based upon the username
    Parameters:
        username: the username from the cookie
    Returns:
        json view record
    '''
    query = {
        "selector": {
            "login": {
                "$eq": username
            }
        },
        "fields": ["login", "views", "_id", "_rev"]
    }
    r = post('users/_find', query, usersDbAuth, jsonContentHeaders, 200)
    if (len(r.json()["docs"]) != 1):
        raise Exception("Error loading user '" + username + "'")
    return r.json()["docs"][0]


def saveUser(user):
    '''
    Purpose:
        Updates existing user record in db
    Parameters:
        user: id of existing user from DB
    Returns:
        n/a
    '''
    put("users/" + user['_id'], user, usersDbAuth)
