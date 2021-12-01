from pandas.core.frame import DataFrame
import requests
import json
import pandas as pd
import numpy as np
import sqlite3
import sqlalchemy
import time

ENDPOINT_URL = "https://apis.alpha.art/api/v1/collection"
engine = sqlalchemy.create_engine('sqlite:///my_lite_store.db', echo=False)



def updatePricing(data_name):
    asset_headers = ['token_id', 'sol_price']
    df = pd.DataFrame(columns = asset_headers)
    next_page = ""
    res=[]

    payload = {
        "collectionId": "skyline",
        "orderBy": "RECENTLY_LISTED",
        "status": [
        "BUY_NOW"
        ],
        "traits": [],
        "limit":1000
    }

    while True:
        response = requests.post(ENDPOINT_URL, data=json.dumps(payload)).json()
        res = res + response['tokens']
        
        if "nextPage" in response:
            payload = {"token": response["nextPage"]}
        else:
            break
        

    for asset in res:
        asset_data = {
            'token_add': asset['mintId'],
            'sol_price': float(asset['price'])/1000000000
        }
        df = df.append(asset_data, ignore_index=True)
    
    con = engine.raw_connection()
    cur = con.cursor()
    query = """UPDATE `{table}` SET `price` = ''""".format(table=data_name)
    res = cur.execute(query)
    df.to_sql('price', con, if_exists='replace')
    
    query = """UPDATE `{table}` SET price = (select price.sol_price from price WHERE price.token_add = `{table}`.address)""".format(table=data_name)
    print(query)
    cur.execute(query)
    #cur.execute("""DELETE FROM `price`""")
    con.commit()
    cur.close()
    con.close()
    

def checkSnipes(rowData):
    for i in range (4, 8):
        con = engine.raw_connection()
        cur = con.cursor()
        maxIdx, minIdx = 0,0
        if i == 2: maxIdx = 5
        if i == 3: maxIdx, minIdx=10,5
        if i == 4: maxIdx, minIdx = 20,10
        if i == 5: maxIdx, minIdx = 50,20
        if i == 6: maxIdx, minIdx = 200,50
        query = """SELECT * FROM `{table}` WHERE price*1.0 <= {max_price} AND (`index` BETWEEN {min} AND {max}) """.format(table=rowData[1], max_price=int(rowData[i]), max = maxIdx, min = minIdx)
        cur.execute(query)
        res = cur.fetchall()
        cur.close()
        con.close()
        if res == None:
            continue
        else:
            for row in res:
                output = ("Token:"+ str(row[1])).ljust(30) + " | Rank:" + str(row[0]).ljust(6) + " | Price:" + str(row[2]).ljust(5)
                print(output)
        


while True:
    updatePricing("skyline")
    time.sleep(10)

#cur.execute("DROP TABLE price")

#returnCollectionAssets('')





