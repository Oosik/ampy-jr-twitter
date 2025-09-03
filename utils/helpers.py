import sys, os
import requests

def is_dev():
    """
    Checks if the bot is running in dev mode or not.
    """
    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        return True
    return False


def run_curl(url, headers=None):
    """
    Make a GET request to the given URL and return a JSON response.
    
    Parameters
    ----------
    url : str
        The URL to query.
    headers : dict
        A dictionary of headers to pass to the request.
    
    Returns
    -------
    data : dict
        A dictionary of the JSON response, or {'Status': 'Error', 'Message': <error message>} if the request fails.
    """
    
    ##
    ## attempt to get data from API
    ## if it fails, return error message
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {'Status': 'Error', 'Message': 'Error: likely due to rate limiting, sit tight for 2 minutes & try again.'}

    ##
    ## check for 200 response
    # response.status_code = 403
    if response.status_code != 200:
        return {'Status': 'Error', 'Message': f"Error fetching data from API. Status: {response.status_code}. Please alert an admin."}
    
    ##
    ## parse the JSON response
    data = response.json()
    return data

def get_alchemy_key():
    """
    Retrieves the Alchemy API key from the environment variables.

    Returns
    -------
    str
        The Alchemy API key from the environment variables.
    """
    return get_env('ALCHEMY_KEY')

def get_etherscan_key():
    """
    Retrieves the Etherscan API key from the environment variables.

    Returns
    -------
    str
        The Etherscan API key from the environment variables.
    """
    return get_env('ETHERSCAN_KEY')

def get_env(value):
    """
    Retrieves the value of an environment variable.

    Parameters
    ----------
    value : str
        The name of the environment variable to retrieve.

    Returns
    -------
    str
        The value of the environment variable, or None if the variable does not exist.
    """
    return os.getenv(value)


def human_readable(num):
    """
    Convert large numbers to human-readable format with K, M, B suffixes.
    
    Parameters
    ----------
    num : float or decimal.Decimal
        The number to convert to human-readable format.
        
    Returns
    -------
    str
        The number formatted with appropriate suffix (K, M, B) or as-is for smaller values.
    """
    ##
    ## Convert to float if it's a string
    if isinstance(num, str):
        try:
            num = float(num)
        except ValueError:
            return num
            
    ##
    ## Convert to float if it's a Decimal
    if hasattr(num, 'as_tuple'):
        num = float(num)
    
    ##
    ## Handle negative numbers by preserving the sign
    negative = num < 0
    abs_num = abs(num)
    
    if abs_num >= 1e9:
        result = f"{abs_num/1e9:.1f}B"
    elif abs_num >= 1e6:
        result = f"{abs_num/1e6:.1f}M"
    elif abs_num >= 1e3:
        result = f"{abs_num/1e3:.1f}K"
    else:
        result = f"{abs_num:.0f}"
    
    ##
    ## Remove .0 if it ends with .0
    if result.endswith('.0B') or result.endswith('.0M') or result.endswith('.0K'):
        result = result[:-3] + result[-1]
    
    ##
    ## Add negative sign if original number was negative
    return f"-{result}" if negative else result


def get_sign(a, b):
    """
    Get the sign of the difference between two numbers.
    """
    if a > b:
        return "+"
    else:
        return "-"