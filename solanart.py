from pandas.core.frame import DataFrame
import requests
import json
import pandas as pd
import numpy as np
import sqlite3
import sqlalchemy
import time

ENDPOINT_URL = "https://qzlsklfacc.medianetwork.cloud/nft_for_sale?collection="
engine = sqlalchemy.create_engine('sqlite:///my_lite_store.db', echo=False)


def returnCollectionAssets(contractAddress, solanartAddress):
    asset_headers = ['token_id', 'sol_price']
    df = pd.DataFrame(columns = asset_headers)

    response = requests.request("GET", ENDPOINT_URL + solanartAddress).json()
    df1 = DataFrame(response)
    #DataFrame.to_excel(response, "test.xlsx")
    for asset in response:
        asset_data = {
            'token_add': asset['token_add'],
            'sol_price': asset['price']
        }
        attributes_raw = asset['attributes']
        attributes_raw = attributes_raw.split(',')
        for splice in attributes_raw:
            slice = splice.split(':')
            if(slice[0] not in df):
                asset_headers.append(slice[0])
                df = df.reindex (columns = asset_headers)
            asset_data[slice[0]] = slice[1].strip()
        df = df.append(asset_data, ignore_index=True)
    df = df.fillna('null')
    df = df.replace(r'^\s*$', np.NaN, regex=True)

    #df.to_sql('.test', con=engine)
    #df.to_excel('LunariaPrices.xlsx')

def updatePricing(data_name, collection_name):
    print(collection_name)
    if collection_name == None: return
    asset_headers = ['token_id', 'sol_price']
    df = pd.DataFrame(columns = asset_headers)
    try:
        #print(ENDPOINT_URL + str(collection_name))
        response = requests.request("GET", ENDPOINT_URL + collection_name).json()
    except:
        print(ENDPOINT_URL + collection_name)
        print("error")
        return
    for asset in response:
        asset_data = {
            'token_add': asset['token_add'],
            'sol_price': asset['price']
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
    for i in range (4, 9):
        con = engine.raw_connection()
        cur = con.cursor()
        maxIdx, minIdx = 0,0
        if i == 4: maxIdx = 5
        if i == 5: maxIdx, minIdx=10,5
        if i == 6: maxIdx, minIdx = 20,10
        if i == 7: maxIdx, minIdx = 50,20
        if i == 8: maxIdx, minIdx = 200,50
        query = """SELECT * FROM `{table}` WHERE price*1.0 <= {max_price} AND (`score_rank` BETWEEN {min} AND {max}) """.format(table=rowData[3], max_price=int(rowData[i]), max = maxIdx, min = minIdx)
        cur.execute(query)
        res = cur.fetchall()
        cur.close()
        con.close()
        if res == None:
            continue
        else:
            for row in res:
                output = ("Token:"+ str(row[2])).ljust(30) + " | Rank:" + str(row[1]).ljust(6) + " | Price:" + str(row[3]).ljust(5)
                print(output)
        

config = pd.read_csv("solanartconfig.csv")
while True:
    for i, row in config.iterrows():
        updatePricing(row['data_name'], row['solanart_name'])
        checkSnipes(row)
    time.sleep(10)

#cur.execute("DROP TABLE price")

#returnCollectionAssets('')





