import json
import httpx

class IPFS:
    def __init__(self, url):
        self._url = url

    def pin_json(self, data):
        url = '{}/api/v0/add?pin=true'.format(self._url)
        resp = httpx.post(url, files={'path': json.dumps(data, separators=(',', ':') )})
        return resp.json()['Hash']
