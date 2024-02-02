import json

WALLET_DATA_PATH = 'wallet_data.xlsx'
SHEET_NAME = 'evm'
ENCRYPTED_DATA_PATH = 'encrypted_data.txt'

with open('data/rpc.json') as file:
    RPC = json.load(file)

with open('data/abi/starrynift/pass_abi.json', 'r') as file:
    PASS_ABI = json.load(file)

with open('data/abi/starrynift/daily_abi.json', 'r') as file:
    DAILY_ABI = json.load(file)

PASS_CONTRACT = '0xe364a4b0188ab22dc13718993b0fa0ca5f123edc'
DAILY_CONTRACT = '0xE3bA0072d1da98269133852fba1795419D72BaF4'

CHAINS_OKX = {
    'linea': 'Linea',
    'base': 'Base',
    'arbitrum': 'Arbitrum One',
    'optimism': 'Optimism',
    'zksync': 'zkSync Era',
    'bsc': 'BSC'
}

placeholder = """████████╗██████╗  █████╗ ██████╗ ██╗██╗   ██╗███╗   ███╗
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║██║   ██║████╗ ████║
   ██║   ██████╔╝███████║██║  ██║██║██║   ██║██╔████╔██║
   ██║   ██╔══██╗██╔══██║██║  ██║██║██║   ██║██║╚██╔╝██║
   ██║   ██║  ██║██║  ██║██████╔╝██║╚██████╔╝██║ ╚═╝ ██║
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝ ╚═════╝ ╚═╝     ╚═╝"""
