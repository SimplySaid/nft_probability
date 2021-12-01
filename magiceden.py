import requests
import json
import pandas as pd
import numpy as np
import sqlite3
import sqlalchemy
import time
from joblib import Parallel, delayed
from tqdm import tqdm

_DEFAULT_RETRY = (
    requests.exceptions.ConnectionError, 
    requests.exceptions.ProxyError, 
    requests.exceptions.ReadTimeout
)

engine = sqlalchemy.create_engine('sqlite:///my_lite_store.db', echo=False)

def getCollectionsPrice(data, dataName):
    asset_headers = ['token_id', 'sol_price']
    df = pd.DataFrame(columns = asset_headers)
    # limit = 0
    # res = []
    # while True: 
    #     endpoint = "https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q={\"$match\":{\"collectionSymbol\":\"%s\"},\"$sort\":{\"createdAt\":-1},\"$skip\":%s,\"$limit\":10000}" % (collectionName, limit)
    #     call = requests.request("GET", endpoint)
    #     if (call != None):
    #         call = call.json()
    #     else:
    #         continue
    #     if call['results'] == []:
    #         break
    #     res = res + call['results']
    #     limit+=200

    res = []
    for list in data:
        res += list

    for asset in res:
        asset_data = {
            'token_id': asset['title'],
            'sol_price': asset['price']
        }
        df = df.append(asset_data, ignore_index=True)
    df = df.fillna('null')
    df = df.replace(r'^\s*$', np.NaN, regex=True)

    con = engine.raw_connection()
    cur = con.cursor()

    df.to_sql('price', con, if_exists='replace')

    query = """UPDATE {table} SET price = (select price.sol_price from price WHERE price.token_id = {table}.token_id)""".format(table=dataName)
    cur.execute(query)
    con.commit()
    cur.close()
    con.close()

def getMarketplaceNFTData(nft_marketplace_name, page, limit=200):
    endpoint = "https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q={\"$match\":{\"collectionSymbol\":\"%s\"},\"$sort\":{\"createdAt\":-1},\"$skip\":%s,\"$limit\":%s}" % (nft_marketplace_name, page, limit)
    print(endpoint)
    call = requests.request("GET", endpoint)
    if (call != None):
        return call.json()['results']
    else:
        return None

def checkSnipes():
    for i in range (2, 7):
        con = engine.raw_connection()
        cur = con.cursor()
        maxIdx, minIdx = 0,0
        if i == 2: maxIdx,pr = 5,100
        if i == 3: maxIdx, minIdx, pr=10,5,50
        if i == 4: maxIdx, minIdx,pr = 20,10,25
        if i == 5: maxIdx, minIdx,pr = 50,20,15
        if i == 6: maxIdx, minIdx,pr = 200,50,10
        query = """SELECT * FROM `{table}` WHERE price*1.0 <= {max_price} AND (`index` BETWEEN {min} AND {max}) """.format(table="Frog", max_price=int(pr), max = maxIdx, min = minIdx)
        #print(query)
        cur.execute(query)
        res = cur.fetchall()
        if res == None:
            continue
        else:
            for row in res:
                output = ("Token:"+ str(row[1])).ljust(30) + " | Rank:" + str(row[0]).ljust(6) + " | Price:" + str(row[2]).ljust(5)
                print(output)
        cur.close()
        con.close()

# while True:
data = Parallel(n_jobs=20)(delayed(getMarketplaceNFTData)("cyber_technicians", skip) for skip in tqdm(range (0, 4000, 200)))
getCollectionsPrice(data,"CyberTechnician")