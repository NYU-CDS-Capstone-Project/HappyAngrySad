#!/usr/bin/python

import json
import requests


API_KEY = "AIzaSyCdQbLORhF7PGVJ7DG1tkoVJGgDYwA_o0M"

r = requests.get("https://www.googleapis.com/youtube/v3/videos?part=statistics&id=" + '3ZqPaohVjmw' + "&key=" + API_KEY)
r = requests.get("https://www.googleapis.com/youtube/v3/videos?part=snippet&id=" + '3ZqPaohVjmw' + "&key=" + API_KEY)
print r.json()