from web3 import Web3
import requests
from termcolor import cprint
import time
import json
import random
import ABI
import threading

factor = 1
number_of_threads = 1

RPC = {
    # '1': '',
    # '3': '',
    '10': 'https://mainnet.optimism.io',
    '56': 'https://bsc-dataseed.binance.org',
    '137': 'https://polygon-rpc.com',
    '42161': 'https://arb1.arbitrum.io/rpc',
    # '43114': '',  # https://support.avax.network/en/articles/4626956-how-do-i-set-up-metamask-on-avalanche
}

swaps_1inch = [
    {'address': '0xd3f1Da62CAFB7E7BC6531FF1ceF6F414291F03D3',
     'symbol': 'DBL',
     'amount': (round(random.uniform(0.0006, 0.00091), 8))*factor},

    {'address': '0x289ba1701C2F088cf0faf8B3705246331cB8A839',
     'symbol': 'LPT',
     'amount': (round(random.uniform(0.0006, 0.00091), 8))*factor},

    {'address': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
     'symbol': 'USDT',
     'amount': (round(random.uniform(0.0006, 0.00091), 8))*factor},

    {'address': '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
     'symbol': 'USDC',
     'amount': (round(random.uniform(0.0006, 0.00091), 8))*factor},

    {'address': '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
     'symbol': 'DAI',
     'amount': (round(random.uniform(0.0006, 0.00091), 8))*factor}
]


def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"] * decimal)))


def get_api_call_data(url):
    try:
        call_data = requests.get(url)
    except Exception as ex:
        print(ex)
        return get_api_call_data(url)
    try:
        api_data = call_data.json()
        return api_data
    except Exception as ex:
        print(ex)
        print(call_data.text)


def inch_swap(_privatekey, _amount_to_swap, fromTokenAddress, _to_symbol):
    account = web3.eth.account.privateKeyToAccount(_privatekey)
    address_wallet = account.address
    try:
        amount = intToDecimal(_amount_to_swap, 18)
        _1inchurl = f'https://api.1inch.io/v4.0/42161/swap?fromTokenAddress={to_token_address}&toTokenAddress=\
{fromTokenAddress}&amount={amount}&fromAddress={address_wallet}&slippage=1'
        json_data = get_api_call_data(_1inchurl)
        nonce = web3.eth.getTransactionCount(address_wallet)
        tx = json_data['tx']
        tx['nonce'] = nonce
        tx['to'] = Web3.toChecksumAddress(tx['to'])
        tx['gasPrice'] = int(tx['gasPrice'])
        tx['value'] = int(tx['value'])
        signed_tx = web3.eth.account.signTransaction(tx, _privatekey)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        cprint(f'\n>>> Swap {_to_symbol} : https://arbiscan.io/tx/{web3.toHex(tx_hash)}', 'green')
        print(f'    {address_wallet}')
    except Exception as error:
        cprint(f'\n>>> Ошибка | {address_wallet} | {_to_symbol} | {error}', 'red')


def inch_swap_approve(_privatekey, amount, _fromTokenAddress, _to_symbol):
    account = web3.eth.account.privateKeyToAccount(_privatekey)
    address_wallet = account.address
    try:
        url = f'https://api.1inch.io/v4.0/42161/approve/transaction?tokenAddress={_fromTokenAddress}&amount={amount}'
        json_data = get_api_call_data(url)
        nonce = web3.eth.getTransactionCount(address_wallet)
        tx = {
            "nonce": nonce,
            "to": web3.toChecksumAddress(json_data["to"]),
            "data": json_data["data"],
            "gasPrice": web3.eth.gas_price,
            "gas": gasLimit,
        }

        signed_tx = web3.eth.account.signTransaction(tx, _privatekey)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        cprint(f'\n>>> approve {_to_symbol} : https://arbiscan.io/tx/{web3.toHex(tx_hash)}', 'green')
        print(f'    {address_wallet}')
    except Exception as error:
        cprint(f'\n>>> Ошибка | {address_wallet} | {_to_symbol} | {error}', 'red')


def inch_swap_sell(_privatekey, fromTokenAddress, to_symbol_):
    global to_token_address
    account = web3.eth.account.privateKeyToAccount(_privatekey)
    address_wallet = account.address
    try:
        if to_symbol_ == 'DBL':
            abi = ABI.ABI_DBL
        elif to_symbol_ == 'LPT':
            abi = ABI.ABI_LPT
        elif to_symbol_ == 'USDT':
            abi = ABI.ABI_USDT
        elif to_symbol_ == 'USDC':
            abi = ABI.ABI_USDT
        elif to_symbol_ == 'DAI':
            abi = ABI.ABI_DAI
        else:
            return
        token = web3.eth.contract(address=fromTokenAddress, abi=abi)  # declaring the token contract
        token_balance = token.functions.balanceOf(address_wallet).call()
        amount = token_balance
        inch_swap_approve(_privatekey, amount, fromTokenAddress, to_symbol_)
        time.sleep(random.randint(10, 15))
        _1inchurl = f'https://api.1inch.io/v4.0/42161/swap?fromTokenAddress={fromTokenAddress}&toTokenAddress=\
{to_token_address}&amount={amount}&fromAddress={address_wallet}&slippage=3'
        json_data = get_api_call_data(_1inchurl)
        nonce = web3.eth.getTransactionCount(address_wallet)
        tx = json_data['tx']
        tx['nonce'] = nonce
        tx['to'] = Web3.toChecksumAddress(tx['to'])
        tx['gasPrice'] = int(tx['gasPrice'])
        tx['value'] = int(tx['value'])
        signed_tx = web3.eth.account.signTransaction(tx, _privatekey)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        cprint(f'\n>>> Sell {to_symbol_} : https://arbiscan.io/tx/{web3.toHex(tx_hash)}', 'green')
        print(f'    {address_wallet}')
    except Exception as error:
        cprint(f'\n>>> Ошибка | {address_wallet} | {to_symbol_} | {error}', 'red')


if __name__ == "__main__":
    cprint(f'\n============================================ Wiedzmin.eth =============================================',
           'cyan')
    cprint(f'\nSubscribe to us : https://t.me/developercode1', 'magenta')
    with open("private_keys.txt", "r") as f:
        keys_list = [row.strip() for row in f]
    ChainUrl = "https://arb1.arbitrum.io/rpc"
    web3 = Web3(Web3.HTTPProvider(ChainUrl))
    gasLimit = 4000000
    to_token_address = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"  # ETH

    def main():
        while keys_list:
            privatekey = keys_list.pop(0)
            random.shuffle(swaps_1inch)
            cprint(f'\n=============== start : {privatekey} ===============', 'white')

            for swap in swaps_1inch:
                amount_to_swap = swap['amount']
                from_token_address = swap['address']
                to_symbol = swap['symbol']
                inch_swap(privatekey, amount_to_swap, from_token_address, to_symbol)
                time.sleep(random.randint(20, 30))
                inch_swap_sell(privatekey, from_token_address, to_symbol)

    for i in range(number_of_threads):
        thred = threading.Thread(target=main).start()
