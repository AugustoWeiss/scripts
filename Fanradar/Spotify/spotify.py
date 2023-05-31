from const import CLIENT_ID, CLIENT_SECRET, SPOTIFY_API_TOKEN_URL, SPOTIFY_API_URL
from urllib.parse import urlencode
import requests
import json
import re


class Spotify(object):
    def __init__(self):
        self._requests = requests.Session()
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
        }
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        res = self._requests.post(SPOTIFY_API_TOKEN_URL, params=urlencode(params), headers=headers, data=params)
        if res.ok:
            response = res.json()
            return response['access_token']

    def make_path(self, path, params=None):
        params = params or {}
        if not (re.search(r"^\/", path)):
            path = "/" + path
        path = SPOTIFY_API_URL + path
        if params:
            path = path + "?" + urlencode(params)
        return path

    # REQUEST METHODS
    def get(self, path, params=None):
        params = params or {}
        headers = {
            'Authorization': "Bearer %s" % self.access_token
        }
        uri = self.make_path(path)
        response = self._requests.get(uri, params=urlencode(params), headers=headers)
        return response

    # UTILS REQUEST
    def get_artist_by_id(self, id):
        res = self.get('artists/%s' % id)
        return res.json() if res.ok else False

    def get_related_artists(self, artist_id):
        res = self.get('artists/%s/related-artists' % artist_id)
        return res.json() if res.ok else False
