import requests
import json
import numpy as np

_DEFAULT_RETRY = (
    requests.exceptions.ConnectionError, 
    requests.exceptions.ProxyError, 
    requests.exceptions.ReadTimeout
)
ENDPOINT_URL = "https://weaver.moonrank.app/"
MOONRANK_ENDPOINT = "https://moonrank.app/mints/unirex?since=n8UTq6qoUjsxAUMQHmLrzdg2Afo5n18JYcSsKdcMbwR&seen=11111"

def get_address ():
    response = requests.get(MOONRANK_ENDPOINT).json()
    addresses = list(response['crawl']['mint_list'].keys())
    return addresses


def r_get(session, url, headers=None, params=None, timeout=15, retry=_DEFAULT_RETRY, **kwargs):
    assert isinstance(session, requests.Session)

    success = False
    while not success:
        try:
            response = session.get(url, headers=headers, params=params, timeout=timeout, **kwargs)
            success = True
        except retry as ex:
            print(f"Failure: {ex}, retrying...")
    return response

def get_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
    }
    s = requests.Session()
    s.headers.update(headers)
    resp = r_get(s, url)
    return resp

with open("CyberTechnician-metadata.json") as f:
    jdata = json.load(f)


_data_is_json = True  # READONLY settings variable
def get_nft_data(elem, addresses):
    global _data_is_json
    #if elem['mint'] in addresses:
    poop = get_url(ENDPOINT_URL + elem["image"])
    #else:
    #    return
    #print(poop.json())

    output = dict()


    if _data_is_json and 'application/json' in poop.headers.get('content-type'):
        try:
            output = poop.json()
            output['mint'] = elem['mint']
            #output['creator'] = elem['properties']['creators']
        except:
            output = poop.text
            output['mint'] = elem['mint']
            output['address'] = elem['address']
            print("Data is not json! Set variable _data_is_json = False!!")
    else:
        return None
    return output


from joblib import Parallel, delayed
from tqdm import tqdm

address_list = get_address()
results = Parallel(n_jobs=60)(delayed(get_nft_data)(elem, address_list) for elem in tqdm(jdata))
#results = Parallel(n_jobs=15)(delayed(get_nft_data)(elem) for elem in address_list)


with open("CyberTechnician.json", "w+") as f:
    json.dump(results, f)