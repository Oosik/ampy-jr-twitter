from utils import run_curl
from utils.helpers import get_alchemy_key, get_etherscan_key, human_readable
from web3 import Web3


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

    return_data = []
    for pool in pools:

        pool_contract = Web3.to_checksum_address(pool[1])

        ##
        ## get list of pools and then loop through
        tvl = contract.functions.accountBalances(pool_contract, amp_address).call()

        return_data.append(pool[0])
        return_data.append(pool[1])
        return_data.append(tvl[1])
        return_data.append(int(round((tvl[1] / 1000000000000000000) * amp_price)))
        return_data.append('$' + human_readable(int(round(tvl[1] / 1000000000000000000 * amp_price))))

    return return_data
