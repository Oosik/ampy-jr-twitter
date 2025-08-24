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
    num : float
        The number to convert to human-readable format.
        
    Returns
    -------
    str
        A string representation of the number with appropriate suffix.
        Examples: "100.0B", "2.5M", "50.0K", "123"
        
    Examples
    --------
    >>> human_readable(1000000000)
    '1.0B'
    >>> human_readable(2500000)
    '2.5M'
    >>> human_readable(50000)
    '50.0K'
    >>> human_readable(123)
    '123'
    """
    if num >= 1e9:
        return f"{num/1e9:.1f}B"
    elif num >= 1e6:
        return f"{num/1e6:.1f}M"
    elif num >= 1e3:
        return f"{num/1e3:.1f}K"
    else:
        return f"{num:.0f}"