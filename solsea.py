from pandas.core.frame import DataFrame
import requests
import json
import pandas as pd
import numpy as np
import sqlalchemy
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from sqlalchemy import create_engine

engine = sqlalchemy.create_engine('sqlite:///my_lite_store.db', echo=False)

header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}

ENDPOINT_URL = "https://solsea.io/nft/"
engine = sqlalchemy.create_engine('sqlite:///my_lite_store.db', echo=False)

def getCollectionAddresses(collectionName):
    con = engine.raw_connection()
    cur = con.cursor()

    cur.execute("""SELECT token_id, address FROM {collection} WHERE `index`<200""".format(collection = collectionName))
    #cur.execute("""SELECT token_id, address FROM {collection} WHERE `index`=5519""".format(collection = collectionName))
    
    res = cur.fetchall()

    return res

    # for row in res:
    #     url = ENDPOINT_URL + row[1]
    #     print(url + " " + row[0])
    #     s = requests.Session()
    #     s.headers.update(headers)
    #     response = s.get(url)
    #     soup = BeautifulSoup(response.text, features = 'html.parser')
        
    #     mydivs = soup.find_all("span", {"class": "price__Nft-module_3_W6L"})
    #     #print(mydivs)
    #     if(mydivs == []):
    #         continue
    #         #print("Not Found")
    #     else:
    #         continue
    #         #print(innerHTML(mydivs[0]).decode('utf-8'))

def innerHTML(element):
    """Returns the inner HTML of an element as a UTF-8 encoded bytestring"""
    return element.encode_contents()

def parse (html):
    soup = BeautifulSoup(html, features = 'html.parser')
    with open("Output.txt", "w", encoding='utf-8') as text_file:
        text_file.write(str(soup))
    
    mydivs = soup.find_all("span", {"class": "price__Nft-module_3_W6L"})
    if(mydivs == []):
        return("Not Found")
    else:
        return innerHTML(mydivs[0]).decode('utf-8')

async def get_nft_data(session, address):
    url = ENDPOINT_URL + address
    async with session.get(url) as response:
        return await response.text()

async def fetch_and_parse (session, id, url):
    print(url)
    html = await get_nft_data(session, url)
    paras = parse(html)
    return [id, paras]
        
async def main(data_name):
    addresses = getCollectionAddresses("solameleon")
    async with aiohttp.ClientSession() as session:
        session.headers.update(header)
        tasks = []
        for id, address in addresses:
            task = asyncio.ensure_future(fetch_and_parse(session, id, address))
            tasks.append(task)
        
        result = await asyncio.gather(*tasks)

    con = engine.raw_connection()
    cur = con.cursor()
    df = DataFrame(result, columns =  {'token_id', 'sol_price'})
    df.to_sql('price', con, if_exists='replace')
    query = """UPDATE `{table}` SET price = (select price.sol_price from price WHERE price.token_id = `{table}`.token_id)""".format(table=data_name)
    cur.execute(query)
    con.commit()
    cur.close()
    con.close()

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main("Solameleon"))