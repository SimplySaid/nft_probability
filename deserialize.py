import json
import base64
import base58
import struct
import requests
from typing import NamedTuple

class Creator(NamedTuple):
    Address: str
    Verified: bool
    Share: int

class Data(NamedTuple):
    Name: str
    Symbol: str
    Uri: str
    SellerFeeBasisPoints: int
    Creators: list

class Metadata(NamedTuple):
    Key: int
    UpdateAuthority: str
    Mint: str
    Data: Data
    PrimarySaleHappened: bool
    IsMutable: bool
    EditionNonce: int

def decode_rust_string(buffer: bytes, offset: int, isascii=True):
    ssize_r = struct.unpack("I", buffer[offset:(offset+4)])
    ssize = ssize_r[0]  # ssize_r=(ssize,)
    data = buffer[(offset+4):(offset+ssize+4)]
    if isascii:
        data_str = data.decode("ascii")
    else:
        data_str = data
    return data_str, ssize + 4  # sizeof uint is 4

def deserialize(s: str) -> str:
    """metadata struct:
    Key                     uchar
    UpdateAuthority         pubkey (4 bytes)
    Mint                    pubkey (4 bytes)
    Data                    Data
    PrimarySaleHappened     bool
    IsMutable               bool
    EditionNonce            *uint8

    Data struct:
    Name                    string
    Symbol                  string
    Uri                     string
    SellerFeeBasisPoints    uint16
    Creators                *[]Creator

    Creator struct:
    Address                 pubkey (4 bytes)
    Verified                bool
    Share                   uint8
    """
    b = base64.b64decode(s)
    key_r = struct.unpack("B", b[:1])
    key = key_r[0]  # key_r = (key,)
    ua = base58.b58encode(b[1:33]).decode("ascii")
    mint = base58.b58encode(b[33:65]).decode("ascii")

    name, name_offset = decode_rust_string(b, 65)
    symbol, symbol_offset = decode_rust_string(b, 65 + name_offset)
    uri, uri_offset = decode_rust_string(b, 65 + symbol_offset + name_offset)

    new_offset = 65 + symbol_offset + name_offset + uri_offset
    sfbp = struct.unpack("H", b[new_offset:(new_offset+2)])[0]
    new_offset += 2

    # creators pointer
    creators_pt = struct.unpack("B", b[new_offset:(new_offset+1)])[0]
    new_offset += 1

    # unpack creators
    size = struct.unpack("I", b[new_offset:(new_offset+4)])[0]
    new_offset += 4
    creators = list()
    creators_out = list()
    for _ in range(size):
        c = dict()
        c["Address"] = base58.b58encode(b[new_offset:(new_offset+32)]).decode("ascii")
        new_offset += 32
        c["Verified"] = struct.unpack("?", b[new_offset:(new_offset+1)])[0]
        new_offset += 1
        c["Share"] = struct.unpack("B", b[new_offset:(new_offset+1)])[0]
        new_offset += 1
        creators.append(c)
        creators_out.append(
            #Creator(c["Address"], c["Verified"], c["Share"])
            {
                'address' : c["Address"],
                'verified' : c["Verified"]
            }
        )

    

    primary_sale_happened = struct.unpack("?", b[new_offset:(new_offset+1)])[0]
    new_offset += 1
    is_mutable = struct.unpack("?", b[new_offset:(new_offset+1)])[0]
    new_offset += 1

    # creators pointer
    edition_pt = struct.unpack("B", b[new_offset:(new_offset+1)])[0]
    new_offset += 1
    edition_nonce = struct.unpack("B", b[new_offset:(new_offset+1)])[0]
    new_offset += 1

    #
    #  post processing
    # 
    def remove_x00(s:str) -> str:
        return s.replace(b"\x00".decode("ascii"), "")
    uri = remove_x00(uri)
    name = remove_x00(name)
    symbol = remove_x00(symbol)

    # create data struct with creators list of structs inside
    #data_out = Data(name, symbol, uri, sfbp, creators_out)
    data_out = {
        'name': name, 
        'symbol': symbol, 
        'uri' : uri, 
        'sfbp' :sfbp, 
        'creators_out' : creators_out
    }

    #metadata_out = dict(key, ua, mint, data_out, primary_sale_happened, is_mutable, edition_nonce)
    metadata_out = {
        'key' : key, 
        'ua' :ua, 
        'mint': mint,
        'data_out': data_out, 
        'primary_sale_happened': primary_sale_happened, 
        'is_mutable': is_mutable, 
        'edition_nonce' : edition_nonce
    }

    if False:
        print(f"""key={key}
mint={mint}
ua={ua}
name={name}
symbol={symbol}
uri={uri}
sfbp={sfbp}
*creators={creators_pt}
creators={creators}
primary_sale_happened={primary_sale_happened}
is_mutable={is_mutable}
*edition_nonce={edition_pt}
edition_nonce={edition_nonce}
"""
    )
    # print(b[new_offset:])
    # possibly some leftover shit
    
    return metadata_out

def deserialize_handler(d: dict) -> str:
    return deserialize(d["account"]["data"][0])

output = []
temp_output = []
creator_list = dict()

def set_wide_analysis(data):
    #with open("kam1_analysis.txt", "w") as f:
    for i in range(len(data["result"])):
        res = deserialize_handler(data['result'][i])
        for row in res['data_out']['creators_out']:
            if (row['verified'] == True):
                verified_address = row['address']
                if verified_address not in creator_list:
                    creator_list[verified_address] = 1
                else:
                    creator_list[verified_address] += 1
        temp_output.append([verified_address, res])

    
    # creators = []
    # for row in temp_output:
    #     if row[0] == max(creator_list, key=creator_list.get):
    #         print(row[1]['mint'])
    #         r = requests.get(row[1]['data_out']['uri']).json()
    #         creator_data = r['properties']['creators']
    #         for row in creator_data:
    #             creators.append(row['address'])
    #         break

    # print(creators)

    #Compare it to the most popular verified creator... doesn't work for multiple creators
    #Will need to check through mint authority
    for row in temp_output:
        if row[0] == max(creator_list, key=creator_list.get):
            output.append(row[1])
        else:
            #print(row[1]['mint'])
            continue

    with open('testoutput.json', 'w') as f:
        json.dump(temp_output, f)

    print(len(output))
    print(creator_list)

    #print(creator_list)


    #print(json.dumps(output))


with open("output_KAM1.json", "r") as f:
    data = json.load(f)

# print(deserialize_handler(data['result'][1]))
set_wide_analysis(data)