import solana
import json
from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client  # synchronous
from solana.rpc.types import MemcmpOpts
import base58
import base64
import asyncio
import spl.token._layouts as layouts
from solana.publickey import PublicKey

MAINNET = "http://api.mainnet-beta.solana.com"
METAPLEX_PUBKEY = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"

def getProgramAccounts(client: Client, name: str, symbol: str):
    b58name = base58.b58encode(name).decode("ascii")
    b58symbol = base58.b58encode(symbol).decode("ascii")
    result = client.get_program_accounts(
        METAPLEX_PUBKEY,
        memcmp_opts=[
            MemcmpOpts(offset=69, bytes=b58name),
            MemcmpOpts(offset=105, bytes=b58symbol)
        ],
        encoding='base64'
    )
    return result

SECURITY_NAME = "KAM1"
solana_client = Client(MAINNET)
#results = getProgramAccounts(solana_client, SECURITY_NAME, "KAM1")

test = solana_client.get_account_info(
    "JBtcDBr8TPWeop5i2BdL2Qjrt9mvKdCEbj97ejpdsqtb",
    encoding='base64'
)

#print(test)

# for res in results['result']:
#     data = layouts.MINT_LAYOUT.parse(solana.utils.helpers.decode_byte_string(res['account']['data'][0]))
#     print(data)
#     decoded_data = dict()
#     for key, value in data.items():
#         if key == "_io":
#             continue
#         elif type(value) == bytes:
#             value = PublicKey(value)
#         decoded_data[key] = str(value)
#     res['account']['data'] = decoded_data
#     #print(res)
# print(results)

# with open(f"output2_{SECURITY_NAME}.json", "w+") as f:
#     json.dump(results['result'], f)




mint_data = layouts.ACCOUNT_LAYOUT.parse(solana.utils.helpers.decode_byte_string(test["result"]["value"]["data"][0]))
#test = PublicKey(mint_data.mint)
#print(test)
#print(type(mint_data))
row = dict()
for key, value in mint_data.items():
    if key == "_io":
        continue
    elif type(value) == bytes:
        value = PublicKey(value)
 #       print(value)
    row[key] = value

print(row)
#print(test)
#print(mint_data)

# print(solana.utils.helpers.decode_byte_string(test2, encoding = "base64"))


# #print(solana.utils.helpers.decode_byte_string(test['result']['value']['data']))

# #solana.instruction.decode_data(test)



# # try:
# #     result = results["result"]
# # except Exception as ex:
# #     print(results)
# #     raise ex





# print(f"we found {len(result)} results for {SECURITY_NAME}!")
# print(result[0])