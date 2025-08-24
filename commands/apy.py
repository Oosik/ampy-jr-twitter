from utils import run_curl

def apy():
    url = 'https://api.flexa.co/collateral_pools'

    ##
    ## attempt to get data from API
    ## if it fails, return error message
    data = run_curl(url)
    
    if 'Status' in data and data['Status'] == 'Error':
        return data['Message']

    return data