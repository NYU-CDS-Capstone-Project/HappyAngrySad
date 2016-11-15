import pandas as pd
import numpy as np
import json
import requests
from requests.auth import HTTPBasicAuth
import graphlab as gl
import data


base_url = "https://happyangrysad.cloudant.com/"
jsonContentHeaders = {'content-type': 'application/json'}

usersDbAuth = HTTPBasicAuth(
    'dsterentrandellesserywhy', '79ca3b2eba8d9575d50e8ba75c92ec18260bd487')
emotionsDbAuth = HTTPBasicAuth(
    'wonestedidestrowillygeth', 'e635d215e38d37d2847079c1ae4b9584193e24de')
viewsDbAuth = HTTPBasicAuth(
    'ateryinummothemedenterne', '6e0320b2deac89677bdd580dc48500ad917afc9e')

# def buildDirtyList():
#     # get list of users marked as dirty sorted by people currntly using the app
#     # could it be a
#     if currentUsers is True:
#         # compute recommendations for current users else:
#         # compute recommendation for most recent user


def userGetDirtyUsers():
    # TODO: we need to update this to get users that are marked dirty.
    # buildDirtyList()
    query = {
        "selector": {
            "login": {
                "$eq": 'mattyd2@gmail.com'
            },
            "dirty": {
                "$eq": False
            }
        },
        "fields": ["login", "views"]
    }
    r = data.post('users/_find', query, usersDbAuth, jsonContentHeaders, 200)
    return r.json()["docs"]


def getVidIdsfromViewIds(viewId):
    query = {
        "selector": {
            "_id": {
                "$eq": viewId
            }
        },
        "fields": ["video", "frames"]
    }
    r = data.post('views/_find', query, viewsDbAuth, jsonContentHeaders, 200)
    print r.json()["docs"]
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
                    print('frames')
                    print(frames)
                    wghtLaugh += float(i['totalFrames']) * laughing
                    print('wghtLaugh')
                    print(wghtLaugh)
                    views.append(wghtLaugh / frames)
        userEmotions['user']['laughing'] = views
    print(userEmotions)
    return views

