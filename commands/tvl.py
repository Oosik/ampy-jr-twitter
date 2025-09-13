from utils import run_curl, save_totals, save_tvl
from utils.helpers import get_alchemy_key, get_etherscan_key
from utils.price import get_price
from web3 import Web3
import time
import logging


def tvl():
    amp_price = get_price()

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

    return_data = []
    total_amp_tvl = 0
    total_usd_tvl = 0
    for pool in pools:

        time.sleep(1)
                
        pool_contract = Web3.to_checksum_address(pool[1])

        ##
        ## get list of pools and then loop through
        tvl = contract.functions.accountBalances(pool_contract, amp_address).call()

        pool_data = [
            pool[0],  # name
            pool[1],  # contract address
            tvl[1],   # amp_amount
            int(round((tvl[1] / 1e18) * amp_price))  # usd_value
        ]

        return_data.append(pool_data)

        # return_data.append('$' + human_readable(int(round(tvl[1] / 1e18 * amp_price))))

        total_amp_tvl += tvl[1]
        total_usd_tvl += (tvl[1] / 1e18) * amp_price


    insert_totals_id = save_totals(total_amp_tvl, total_usd_tvl)
    insert_tvl_id = save_tvl(return_data, insert_totals_id)

    return {
        'totals_id': insert_totals_id,
        'tvl_id': insert_tvl_id
    }
