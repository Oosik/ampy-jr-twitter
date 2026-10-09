from utils import run_curl

def get_price():
    ##
    ## get AMP/USD from CoinGecko
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=amp-token&vs_currencies=usd'
    
    ##
    ## attempt to get data from API
    ## if it fails, return error message
    data = run_curl(url)
    
    if 'Status' in data and data['Status'] == 'Error':
        return data['Message']

    try:
        amp_price = float(data['amp-token']['usd'])
    except (KeyError, TypeError, ValueError):
        return 'Error: unexpected CoinGecko price response. Please alert an admin.'

    return amp_price
