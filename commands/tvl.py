from utils import run_curl
from utils.helpers import get_alchemy_key, get_etherscan_key, human_readable, is_dev, get_env
from web3 import Web3
import mysql.connector
from datetime import datetime


def tvl():
    ##
    ## get the price from pyth so it's closer to the value on app.flexa.co
    url = 'https://hermes.pyth.network/v2/updates/price/latest?ids[]=0xd37e4513ebe235fff81e453d400debaf9a49a5df2b7faa11b3831d35d7e72cb7'
    
    ##
    ## attempt to get data from API
    ## if it fails, return error message
    data = run_curl(url)
    
    if 'Status' in data and data['Status'] == 'Error':
        return data['Message']

    amp_price = int(data['parsed'][0]['price']['price']) / (10 ** abs(data['parsed'][0]['price']['expo']))

    ##
    ## attempt to get data from flexa API
    ## if it fails, return error message
    data = run_curl('https://api.flexa.co/collateral_pools')
    
    if 'Status' in data and data['Status'] == 'Error':
        return data['Message']
    
    ##
    ## generate array of names and contract addresses
    pools = []
    for pool in data['data']:
        name = pool['entity']['name']
        
        ##
        ## remove wallet from name
        if 'wallet' in name.lower():
            name = name.replace('Wallet', '').replace('wallet', '').strip()

        id = pool['id']
        ids = id.split(':')
        id = ids[2] 
        
        pools.append([name, id])
        
    ##
    ## URL for the API
    w3 = Web3(Web3.HTTPProvider(f"https://eth-mainnet.g.alchemy.com/v2/{get_alchemy_key()}"))
    anvil_contract = "0x5d2725fdE4d7Aa3388DA4519ac0449Cc031d675f"

    contract_address = Web3.to_checksum_address(anvil_contract)
    
    data = run_curl(f'https://api.etherscan.io/v2/api?chainid=1&module=contract&action=getabi&address=0x5d2725fdE4d7Aa3388DA4519ac0449Cc031d675f&apikey={get_etherscan_key()}')
    
    if 'Status' in data and data['Status'] == 'Error':
        return data['Message']
    
    abi = data['result']

    ##
    ## Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=abi)

    amp_contract = "0xff20817765cb7f73d4bde2e66e067e58d11095c2"

    amp_address = Web3.to_checksum_address(amp_contract)

    if is_dev():
        conn = mysql.connector.connect(
            host = get_env('DEV_DB_HOST'),
            database = get_env('DEV_DB_NAME'),
            user = get_env('DEV_DB_USER'),
            password = get_env('DEV_DB_PASS')
        )
    else:
        conn = mysql.connector.connect(
            host = get_env('DB_HOST'),
            database = get_env('DB_NAME'),
            user = get_env('DB_USER'),
            password = get_env('DB_PASS')
        )

    cursor = conn.cursor()


    return_data = []
    total_amp_tvl = 0
    total_usd_tvl = 0
    for pool in pools:

        pool_contract = Web3.to_checksum_address(pool[1])

        ##
        ## get list of pools and then loop through
        tvl = contract.functions.accountBalances(pool_contract, amp_address).call()

        pool_data = [
            pool[0],  # name
            pool[1],  # contract address
            tvl[1],   # amp_amount
            int(round((tvl[1] / 1000000000000000000) * amp_price))  # usd_value
        ]

        return_data.append(pool_data)

        # return_data.append('$' + human_readable(int(round(tvl[1] / 1000000000000000000 * amp_price))))

        total_amp_tvl += tvl[1]
        total_usd_tvl += (tvl[1] / 1000000000000000000) * amp_price


    cursor.execute('''
        INSERT INTO totals (amp, usd)
        VALUES (%s, %s)
    ''', (total_amp_tvl, total_usd_tvl)
    )
    totals_insert_id = cursor.lastrowid

    for pool_data in return_data:
        cursor.execute('''
            INSERT INTO tvl (name, contract, amp_total, usd, batch_id)
            VALUES (%s, %s, %s, %s, %s)
        ''', (pool_data[0], pool_data[1], pool_data[2], pool_data[3], totals_insert_id)
        )
        

    conn.commit()
    cursor.close()
    conn.close()

    return return_data
