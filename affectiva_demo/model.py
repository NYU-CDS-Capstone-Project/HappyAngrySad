import pandas as pd
import numpy as np
import json
import requests
from requests.auth import HTTPBasicAuth
import graphlab as gl

base_url = "https://happyangrysad.cloudant.com/"
jsonContentHeaders = {'content-type': 'application/json'}

usersDbAuth = HTTPBasicAuth(
    'dsterentrandellesserywhy', '79ca3b2eba8d9575d50e8ba75c92ec18260bd487')
emotionsDbAuth = HTTPBasicAuth(
    'wonestedidestrowillygeth', 'e635d215e38d37d2847079c1ae4b9584193e24de')
viewsDbAuth = HTTPBasicAuth(
    'ateryinummothemedenterne', '6e0320b2deac89677bdd580dc48500ad917afc9e')


def getfiles():
    r = requests.get('https://happyangrysad.cloudant.com/views/_all_docs?include_docs=true',
                     auth=('ateryinummothemedenterne', '6e0320b2deac89677bdd580dc48500ad917afc9e'))
    mydictionary = r.json()
    return mydictionary


def getusers():
    r = requests.get('https://happyangrysad.cloudant.com/users/_all_docs?include_docs=true',
                     auth=('dsterentrandellesserywhy', '79ca3b2eba8d9575d50e8ba75c92ec18260bd487'))
    mydictionary = r.json()
    return mydictionary


def post(url, data, auth, headers, expected_code):
    response = requests.post(
        base_url + url, data=json.dumps(data), auth=auth, headers=headers)
    if response.status_code != expected_code:
        raise Exception("Http error:" + response.text)
    return response


def userGetDirtyUsers():
    # TODO: we need to update this to get users that are marked dirty.
    query = {
        "selector": {
            "login": {
                "$eq": 'alexbakhturin@gmail.com'
            }
        },
        "fields": ["login", "views"]
    }
    r = post('users/_find', query, usersDbAuth, jsonContentHeaders, 200)
    return r.json()["docs"]


def getVidIdsfromViewIds(viewId):
    # TODO: we need to update this to get users that are marked dirty.
    query = {
        "selector": {
            "_id": {
                "$eq": viewId
            }
        },
        "fields": ["video", "frames"]
    }
    r = post('views/_find', query, viewsDbAuth, jsonContentHeaders, 200)
    return r.json()["docs"][0]['frames']


def getContentIds():
    dirtyUsers = userGetDirtyUsers()
    userEmotions = {}
    for dUser in dirtyUsers:
        userEmotions['user'] = {}
        userEmotions['user']['user_id'] = dUser['login']
        views = []
        for viewId in dUser['views']:
            view = getVidIdsfromViewIds(viewId)
            counter = 0
            frames = 0
            for i in view:
                wghtLaugh = 0
                frames += float(i['totalFrames'])
                if 'emojis' in i:
                    # print i
                    laughing = float(i['emojis']['laughing'])
                    print('laughing')
                    print(laughing)
                    wghtLaugh += float(i['totalFrames']) * laughing
                    print('wghtLaugh')
                    print(wghtLaugh)
                    views.append(wghtLaugh / frames)
        userEmotions['user']['laughing'] = views
    return userEmotions


# user_info = gl.SFrame(makeAllUsers(numUsers))
# item_info = gl.SFrame(makeAllContent(numContent))
# item_id | rating | user_id |
# ----------------------------
# 099889  | 0.0089 | 93kd9kj |
# 099889  | 0.0089 | 93kd9kj |
userContentDB = gl.SFrame()

# training_data, validation_data = gl.recommender.util.random_split_by_user(userContentDB, 'user_id', 'item_id')

item_sim_model = gl.item_similarity_recommender.create(
    userContentDB, user_id='id', item_id='videoID', target='rating', similarity_type='pearson')
# item_sim_model = gl.ranking_factorization_recommender.create( training_data , target='rating', user_data = user_info, item_data=item_info )

# Make Recommendations:
item_sim_recomm = item_sim_model.recommend(users=range(1, 6), k=5)
item_sim_recomm.print_rows(num_rows=25)
