import pandas as pd
import numpy as np
import json
import requests
from requests.auth import HTTPBasicAuth
import networkx as nx
import data
from collections import OrderedDict
import random


def getNeigbors(fun, st):
    if st == [] or (st is None):
        return []
    if type(st) == str:
        return fun(st)
    if type(st) == unicode:
        return fun(str(st))
    if type(st) == list and len(st) > 0 and type(st[0]) == list:
        st = st[0]
    # print "ST"
    # print st
    # print type(st)
    final = [fun(item) for item in st]
    if any(isinstance(i, list) for i in final):  # check to see if is a list
        final = [val for sublist in final for val in sublist]  # flatten
    final = list(set(final))  # note this fucks up order
    if final is None:
        return []
    return final


def getImpact(user, content, G):
    newPrediction = []
    impactedPredictions = []
    A = set([user])

    B = set(G.neighbors(content))

    C = set(getNeigbors(G.neighbors, getNeigbors(G.neighbors, user)))
    C.remove(user)
    abcUnion = (A | B | C)
    for someUser in abcUnion:
        before = G.neighbors(someUser)
        before = getNeigbors(G.neighbors, before).remove(someUser)
        before = getNeigbors(G.neighbors, before)
        before = [item for item in before if item not in G.neighbors(someUser)]
        if someUser in A:
            after = getNeigbors(
                G.neighbors, getNeigbors(G.neighbors, content))
            after = [
                item for item in after if item not in G.neighbors(content)]
            after.remove(content)
        elif someUser in B:
            after = set(getNeigbors(G.neighbors, user)) - \
                set(getNeigbors(G.neighbors, someUser))
        elif someUser in C:
            after = content
        for someContent in (set(after) or set(before)):
            impactedPredictions.append((someUser, someContent))
    #     for item in (set(after) - set(before)):
    #         newPrediction.append( (someUser,someContent))
    # return impactedPredictions, newPrediction
    return len(impactedPredictions)


def checkUnwatched(userItemVids):
    allVids = data.getAllContentIds()
    allVidsSet = set()
    for i in allVids:
        allVidsSet.add(str(i['video_id']))
    unWatchedVids = allVidsSet - userItemVids
    return unWatchedVids


def getBestRec(user):
    G = data.getGraph()
    userItemVidObjective = OrderedDict() # for getting top impacted user content pairs
    userItemVids = []
    numImpactedRecs = []
    if user not in G.nodes():
        return
    visited = set(G.neighbors(user))
    userItemVids = set()
    for i in G.nodes(data=True):  # get list of all watched vids
        if i[1]['type'] == 'video':
            userItemVids.add(i[0])
    unWatchedVids = checkUnwatched(userItemVids)
    numUnWatchedVids = len(unWatchedVids)
    if numUnWatchedVids >= 6:
        return random.sample(list(unWatchedVids), 6)
    else:
        for product in list(userItemVids - visited):
            userItemVidObjective[product] = getImpact(user, product, G)
        userItemVnseenvids = userItemVidObjective.keys()
        scores = userItemVidObjective.values()
        sorted_idx = np.argsort(scores)
        sorted_words = [userItemVnseenvids[ii] for ii in sorted_idx[::-1]]
        numRecomsToUse = 6 - numUnWatchedVids
        finalrecs = random.sample(sorted_words[:15], numRecomsToUse) + list(unWatchedVids)
        return finalrecs
