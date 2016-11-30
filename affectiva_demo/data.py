import json
import requests
from requests.auth import HTTPBasicAuth
import networkx as nx
import feature_eng as fe


base_url = "https://happyangrysad.cloudant.com/"
jsonContentHeaders = {'content-type': 'application/json'}

# get data from youtube
API_KEY = "AIzaSyCdQbLORhF7PGVJ7DG1tkoVJGgDYwA_o0M"


usersDbAuth = {
    'test': HTTPBasicAuth(
        'dsterentrandellesserywhy', '79ca3b2eba8d9575d50e8ba75c92ec18260bd487'),
    'prod': HTTPBasicAuth(
        'maytozendeesinglayinglad', '43653cc82f88df89d779477016ebba0981e56fbc'),
}

viewsDbAuth = {
    'test': HTTPBasicAuth(
        'ateryinummothemedenterne', '6e0320b2deac89677bdd580dc48500ad917afc9e'),
    'prod': HTTPBasicAuth(
        'daystryoudeditchersedlys', '74d4ed7505ab3d685b014abec7575611880346ca')
}

userItemDBAuth = {
    'test': HTTPBasicAuth(
        'atentediledithereetyncen', '87646444b19752709b3ccff9c0516c1f0b1511ff'),
    'prod': HTTPBasicAuth(
        'cherhatinistaystandetole', '1dfd59b88787c23c78022ea21d562f88b7e4dfe3')
}

contentDBAuth = {
    'test': HTTPBasicAuth(
        'amessintsmandlestationea', '71d5d6286f8397540b7433f3de2098d77a5daec9'),
    'prod': HTTPBasicAuth(
        'chandsonsidelystingsisud', '68cdd07b4a13d64e99f76109301715f2aff3fa0e')
}


# by default test mode is ON
# to run un the production mode:
# python app.py --env=prod
env = 'test'


def buildUrl(db, url):
    '''
    Purpose:
            Function to create URL and add 'prod' if the production mode is ON
    Parameters:
            db: name of the database
            url: specific function/url ending
    Return:
                URL which could be used in post, get, put methods
        '''

    result = base_url + db
    if env == 'prod':
        result += '_prod'
    if len(url) > 0:
        result += "/" + url
    return result


def post(db, url, data, auth, headers, expected_code):
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
    print "buildUrl(db, url)"
    print buildUrl(db, url)
    response = requests.post(
        buildUrl(db, url), data=json.dumps(data), auth=auth[env], headers=headers)
    if response.status_code != expected_code:
        raise Exception("Http error:" + response.text)
    return response


def get(db, url, auth):
    '''
    Purpose:
        Generic function for creating "GET" URL strings to interact with DB.
    Parameters:
        url: this indicates the specific DB to access and the data to get.
        auth: these are the usernames and keys to the DB
    Returns:
        The DB API response containing data
    '''

    response = requests.get(buildUrl(db, url), auth=auth[env])
    if response.status_code != 200:
        raise Exception("Http error:" + response.text)
    return response


def put(db, url, data, auth):
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

    response = requests.put(
        buildUrl(db, url), data=json.dumps(data), auth=auth[env])
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
    r = post('users', '_find', query, usersDbAuth, jsonContentHeaders, 200)
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
        'views': [],
        'dirty': False
    }
    post('users', '', doc, usersDbAuth, jsonContentHeaders, 201)


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
    r = post('views', '', doc, viewsDbAuth, jsonContentHeaders, 201)
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
    r = get("views", id, viewsDbAuth)
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
    put("views", view['_id'], view, viewsDbAuth)


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
        "fields": ["login", "views", "_id", "_rev", "recommendations"]
    }
    r = post('users', '_find', query, usersDbAuth, jsonContentHeaders, 200)
    if (len(r.json()["docs"]) != 1):
        raise Exception("Error loading user '" + username + "'")
    return r.json()["docs"][0]


def getGraph():
    query = {
        "selector": {
            "_id": {
                "$gt": 0
            }
        },
        "fields": [
            "user_id",
            "video_id"
        ],
    }
    r = post("useritem", "_find", query,
             userItemDBAuth, jsonContentHeaders, 200)
    edges = r.json()['docs']
    usrs, vids = [], []
    for i in edges:
        usrs.append(str(i['user_id']))
        vids.append(str(i['video_id']))
    G = nx.Graph()
    for vid in vids:
        G.add_node(vid, {'type': 'video'})
    for usr in usrs:
        G.add_node(usr, {'type': 'user'})
    for edge in edges:
        G.add_edge(str(edge['user_id']), str(edge['video_id']), {'weight': 1})
    return G


def saveUser(user):
    '''
    Purpose:
        Updates existing user record in db
    Parameters:
        user: id of existing user from DB
    Returns:
        n/a
    '''
    put("users", "/" + user['_id'], user, usersDbAuth)


def getDirtyUsers():
    query = {
        "selector": {
            "dirty": {
                "$eq": True
            }
        },
        "fields": ["login", "_id"]
    }
    r = post('users', '_find', query, usersDbAuth, jsonContentHeaders, 200)
    return r.json()["docs"]


def getAllContentIds():
    query = {
        "selector": {
            "_id": {
                "$gt": 0
            }
        },
        "fields": [
            "video_id","_id","_rev"
        ],
    }
    r = post('content', '_find', query,
             contentDBAuth, jsonContentHeaders, 200)
    return r.json()['docs']


def computeViewStats(view_id):
    '''
    Purpose:
        Compute the summary statistics of the view for easy modeling
    Parameters:
        view_id: the id from the AJAX call for updating the User record
        when the view is finished
    Returns:
        n/a
    '''
    # get view from DB
    view = loadView(view_id)
    # calculate the summary statistics for the view
    stats = fe.computeStats(view)
    # stats = fe.computeStats(view)
    # append view stats to doc
    view['frame_stats'] = stats
    # update view on Cloudant
    put("views", view['_id'], view, viewsDbAuth)
    print(stats)
    return stats


def updateGraph(view_id, user_id):
    '''
    Purpose:
        Create a new document in the Cloudant DB representing the graph
    Parameters:
        view_id: the id from the AJAX call for updating the User record
        when the view is finished
        user_id: the user's id
    Returns:
        n/a
    '''
    view = loadView(view_id)
    video_id = view['video']
    doc = {
        'video_id': video_id,
        'user_id': user_id,
    }
    r = post('useritem', '', doc, userItemDBAuth, jsonContentHeaders, 201)
    if r.status_code != 201:
        raise Exception("Http error:" + r.text)
    print "successfully updated Graph useritem pair"


def postContent(contentData, put =True):
    '''
    Purpose:
        add videos to content DB
    Params:
        video_ids: list of strings
    Returns:
        n/a
    '''
    video_ids = [ item['video_id'] for item in contentData ]
    ids = [ item['_id'] for item in contentData ]
    revs = [ item['_rev'] for item in contentData ]



    for i  in range(len(video_ids)):
        #r = requests.get("https://www.googleapis.com/youtube/v3/videos?part=statistics&snippet&id=" + str(vidID) + "&key=" + API_KEY)
        stats = requests.get("https://www.googleapis.com/youtube/v3/videos?part=statistics&snippet&id=" + str(video_ids[i]) + "&key=" + API_KEY)
        metaData = requests.get("https://www.googleapis.com/youtube/v3/videos?part=snippet&id=" + str(video_ids[i]) + "&key=" + API_KEY)
        stats =  stats.json()['items'][0]["statistics"]
        
        title =  metaData.json()['items'][0]['snippet']['title']
        print "thumbnails"
        thumbnailURL = metaData.json()['items'][0]['snippet']['thumbnails']['medium']['url']
        stats['title'] = title
        stats['video_id'] = str(video_ids[i])
        stats['thumbnail_url'] = thumbnailURL
        if put ==True:
            stats['_rev'] = str(revs[i])
            stats['_id'] = str(ids[i])

        #title =  metaData.json()
        print stats
        createContent(stats)


def createContent(data):
    '''
    Purpose:
        Creates entry for content in content db
    Parameters:
        username: string input by user on /login page
    Returns:
        N/A
    '''
    post('content', '', data, contentDBAuth, jsonContentHeaders, 201)

if __name__ == '__main__':
   
    ids = getAllContentIds()
    postContent(ids)
    # data = ["FGXDKrUoVrw","ccAiiGb7S6k","_OVg8uov78I","hJdF8DJ70Dc","6xncCLKC7gY","SIWLR5g0G74","Fc1P-AEaEp8","WApuXPDR5Q0","1zyQ6c7hNG4","he2a4xK8ctk","HseMjKYs4Ug","cPi6OTCGLF0","BUS6nKpddec","ZZbIx7xy5mc","k5xebCq6lfk","q6I29UlOZSo","A43JOxLa5MM","R97TsVDC1BY","q8DiOthAKek","vkG7FGVWsLA","SEBLt6Kd9EY","G7RgN9ijwE4","d5mK7dzyUkM","vLfAtCbE_Jc","CAbUmTUiVtI","UiyDmqO59QE","8szwlCnKUbY","jmQ4nRbtbTM","sKFpFmQSeGs","B03XxfTl4Uk","QKSMxdsw_ZU","Hree0k9jpTs","Vw4KVoEVcr0","5d7aruKYkKs","PWXigjFm4TM","1hPxGmTGarM","J---aiyznGQ","C_S5cXbXe-4","ssC1JDCXk2M","Fj73JF_bhjc","c8xJtH6UcQY","wMQvCCBbRK4","vNSxargsAWk","VJm-E38G3-0","29Rk9sBdoB8","Wh-gxWpQijw","CliXVjTBMnw","q1LSv468kzI","NsKaCS3CtsY","wEyxE5htfTE","wgTZUU4gJ2U","HrN-GPYlcbQ","KDDN40hHXCQ","YfFko5qhZtY","nTDud03nzCg","uxrTLmruBKk","PaFnO5LKTSs","aS10mmDvDCs","bPWZ7ASnhiE","JDaLg7G8rH0"]
    # postContent(data)

