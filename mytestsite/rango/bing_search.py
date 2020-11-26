import json
import urllib

# Add Microsoft Account Key to a file called bing.key

def read_bing_key():
    """
    reads the BING API key from a file called 'bing.key'.
    returns: a string which is either None or with a key.
    remember: put bing.key in .gitignore file to avoid committing it!
    """
    bing_api_key = None

    try:
        with open('bing.key', 'r') as f:
            bing_api_key = f.readline()
    except:
        raise IOError('bing.key file not found')

    return bing_api_key


def run_query(search_terms):
    """
    given a search terms 
    return a list of results from the Bing search engine.
    """
    bing_api_key = read_bing_key()

    if not bing_api_key:
        raise KeyError("Bing Key Not Found")

    # Specify the base url and the service
    root_url = 'https://api.datamarket.azure.com/Bing/Search/'
    service = 'Web'

    # specify how many results we wish to be returned per page.
    # offset specifies where in the results list to start from.
    # with results_per_page = 10 and offset = 11, this would start from page 2.
    results_per_page = 10
    offset = 0

    # wrap quotes around query terms as required by the Bing API.
    query = "'{0}'".format(search_terms)

    # turn the query into an HTML encoded string, using urllib.
    query = urllib.parse.quote(query)

    # construct teh latter part of our request's RUL.
    # sets the format of the response to JSON and sets other properties.
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
                root_url,
                service,
                results_per_page,
                offset,
                query)

    # setup authentication with the Bing servers.
    # the username MUST be a blank string, and put in your API key.
    username = ''

    # setup a password manager to help authenticate request.
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

    password_mgr.add_password(None, search_url, username, bing_api_key)
    
    results = []

    try:
        # prepare for connecting to Bing's servers.
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)

        # connect to the server and read the response generated.
        response = urllib.request.urlopen(search_url).read()
        response = response.decode('utf-8')

        # convert the string response to a python dictionary object.
        json_response = json.loads(response)

        # loop through each page returned , populatign out results list.
        for result in json_response['d']['results']:
            results.append({'title': result['Title'],
                            'link': result['Url'],
                            'summary': result['Description']})
    except:
        print("Error when querying the Bing API")

    # return the list of results to the calling function.
    return results

