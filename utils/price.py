from utils import run_curl

def get_price():
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

    return amp_price