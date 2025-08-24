import sys
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