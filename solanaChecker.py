from solana.rpc.api import Client
from solana.publickey import PublicKey
solana_client = Client("http://localhost:8002")

solana_client.get_account_info(PublicKey(1)) 
