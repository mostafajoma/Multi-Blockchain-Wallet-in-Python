import subprocess
import json
from constants import *
import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

load_dotenv()


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

mnemonic = os.getenv('MNEMONIC','mnemonic')

 

# create a function for derive wallet
def derive_wallets(mnemonic,coin,numderive):
    command = f'./derive -g --mnemonic="{mnemonic}" --col=path,address,privkey,pubkey,pubkeyhash, --coin="{coin}" --numderive="{numderive}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()

    keys = json.loads(output)
    return keys 


# test the function 
derive_wallets(mnemonic,ETH,3) 

# Create an object
coins = { 'ETH' : derive_wallets(mnemonic,ETH, 3),
         'btc-test' : derive_wallets(mnemonic,BTCTEST, 3)}

# test the object
coins['btc-test'][1]

# create a function that convert the privkey string in a child key to an account object.
def priv_key_to_account(coin,priv_key):
    print(coin)
    print(priv_key)
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    
# create function for raw transaction 
def create_tx(coin,account, recipient, amount):
    if coin == ETH: 
        gasEstimate = w3.eth.estimateGas(
            {"from":eth_acc.address, "to":recipient, "value": amount}
        )
        return { 
            "from": eth_acc.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(eth_acc.address)
        }
    
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])
    
# create a function to hold Ethereum 
eth_acc = priv_key_to_account(ETH, derive_wallets(mnemonic, ETH,5)[0]['privkey'])
  

    
# create a function to send txn
def send_txn(coin,account,recipient, amount):
    txn = create_tx(coin, account, recipient, amount)
    if coin == ETH:
        signed_txn = eth_acc.sign_transaction(txn)
        result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return result.hex()
    elif coin == BTCTEST:
        signed_txn = account.sign_transaction(txn)
        return NetworkAPI.broadcast_tx_testnet(signed_txn)

