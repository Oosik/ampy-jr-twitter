import prettytable as pt
from utils import run_curl

def apy():
    
    """
    Grabs the 7D and 30D APYs for all flexa collateral pools.

    Returns:
        str: A formatted string containing a table of the pools and their
            respective APYs.
    """
    url = 'https://api.flexa.co/collateral_pools'

    ##
    ## attempt to get data from API
    ## if it fails, return error message
    data = run_curl(url)
    
    if 'Status' in data and data['Status'] == 'Error':
        return data['Message']

    return data