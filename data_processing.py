import requests
import json
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

disk_engine = create_engine('sqlite:///my_lite_store.db')

def returnCollections():
    return

def returnCollectionAssets(collection_name, creator):
    token_id = 0
    asset_headers = ['token_id', 'price', 'address']
    df = pd.DataFrame(columns = asset_headers)

    data = open("./raw_json/" + collection_name + '.json',)
    response = json.load(data)

    for asset in response:
        #print(asset['name'])
        # if asset['name'] == "DCBear 2090":
        #     print(asset['properties']['creators'][0]['address'])

        #print(asset['properties']['creators'][0]['address'])
        #print(asset['properties']['creators'][0]['address'])
        if asset == None or asset['properties']['creators'] == [] or asset['properties']['creators'][0]['address'] != creator:
            continue

        if 'attributes' not in asset:
            continue

        asset_data = {
            'token_id': asset['name'],
            'address': asset['mint'],
            'trait_count': len(asset['attributes'])
        }
        #if asset['attributes'][0]['trait_type'] == "Background" and collection_name == "PixelDix": continue
        seen_attributes = []

        for a in asset['attributes']:
            if a['value'] is None or a['value'] == "None":
                asset_data['trait_count'] -= 1

            #asset_data['address'] = a['mint']
            a['trait_type'] = a['trait_type'].lower()
            a['trait_type'] = a['trait_type'].strip()
            a['trait_type'] = a['trait_type'].replace(':', "")
            while (a['trait_type'] in seen_attributes):
                a['trait_type'] = a['trait_type'] + '1'
            seen_attributes.append(a['trait_type'])
            if(a['trait_type'] not in df):
                df[a['trait_type']] = 'None'
            asset_data[a['trait_type']] = a['value']
        df = df.append(asset_data, ignore_index=True)
    
    df = df.fillna('None')
    df = df.replace(r'^\s*$', 'None', regex=True)

    df['score'] = 0
    df['adj_score'] = 0
    df['rarity'] = 1
    for columnName, columnData in df.iteritems(): 
        if columnName not in ('token_id', 'rarity', 'address', 'price', 'score', 'accesories', 'adj_score'):
            # print(df[columnName].value_counts().max())
            traitCount = df.groupby(columnName)[columnName].transform('count')
            df[columnName + ' rarity'] = traitCount / len(df[columnName])
            df['rarity'] = df['rarity'] * df[columnName + ' rarity']
            df[columnName + 'adjscore'] = (1/(traitCount / df[columnName].value_counts().max())).round(4)
            df['score'] = df['score'] + (1/(df[columnName + ' rarity']))
            df['adj_score'] = df['adj_score'] + 1/(traitCount / df[columnName].value_counts().max())

    #df = df.round(5)
    df = df.sort_values(by=['adj_score'], ascending=False, ignore_index= True)
    base_ranking = df['score'].rank(ascending=False).astype(int)
    df.insert(0,"score_rank", base_ranking)
    df.to_sql(collection_name, disk_engine, if_exists='replace')
    df.to_excel(collection_name + '.xlsx')

collections = [
    # 'Waifu',
    # 'EternalBeings',
    # 'RedPanda',
    # 'SolChan',
    # ['2DSoldier',"8tKpJSKcwnPKCyxSpWQm4JeNfY76kWZkbiZcYExzsTvd"]
    # '3DSoldier',
    # 'lunaria',
    # 'Boneworld',
    # 'PixelDix',
    # 'Solfinity',
    # 'Meerkat',
    # 'ShellRacer'
    #'Frog'
    #'GloomPunk'
    #['SolanaBirbs', "H9eiJ9Sa6gZVytbMU4JUwzyLvkeBUmL5oguDhx3CUfEE"]
    #['Solameleon', '3ktoq644v5x3k2jBiNRPwbg5vwwcrgK3SA5HAEFD5yeC']
    # ['KAM1', "EdX5kdnmdwdUpRqQh8zdmvmf3dUaVxBWPwUaezgvsonf"],
    # ['CyberPharmacist', "4K6evwuydiR9WhfRBb6c3GrGMRjKzkDu1n8rTKf16amy"]
    #['SEALZ', "6g8oEzmPYn7mHt5AdWqRBqj142FjDWxWSH9rM2dZRcdE"]
    #['SKYLINE', "2is2NRunEwhotCQrRFXt2w3Fy2Vdo6pasiWzJK4HpcQU"]
    #['Unirexcity', "BPFxj4DSN4r8bJtFzoo3pPmdiAM5aNapNkqHwZxj2vRE"]
    ['CyberTechnician', "9C92nqyGkhG5kD4uYk5E3Hh1GBeW5gq5KBggnjNFJXf9"]

    #['RogueSharks', "AmivaqHeZBgUZkzEZ44Mi9zQJruExZMP4PVRYduFVkaS"]

]

for c in collections:
    returnCollectionAssets(c[0], c[1])





