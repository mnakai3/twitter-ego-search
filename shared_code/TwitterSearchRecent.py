import os
import requests
import json

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
default_query_params = 'lang:ja -is:retweet'
query_keywords = ''
query_params = {
    'query': default_query_params,
    'tweet.fields': 'author_id',
    'expansions': 'author_id',
    'max_results': 10 # between 10 and 100
}

query_response = ''

endpoint_url = "https://api.twitter.com/2/tweets/search/recent"

def append_query_keyword(keyword, cond='OR'):
    global query_params
    params = list(query_params['query'])
    p = len(params)
    if params[-1] == ')':
        p = p - 1
        params.insert(p, f' {cond} {keyword}')
    else:
        params.append(f' ({keyword})')
    query_params['query'] = ''.join(params)

def connect_to_endpoint():
    global bearer_token
    global query_params
    global query_response

    def bearer_oauth(r):
        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2RecentSearchPython"
        return r

    response = requests.get(endpoint_url, auth=bearer_oauth, params=query_params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    query_response = response.json()

def get_permalinks(excludes_users=''):
    global query_response
    if not query_response:
        return None

    def get_username(author_id):
        for u in query_response['includes']['users']:
            if u['id'] == author_id:
                return u['username']
        return None

    permalinks = []
    if query_response['meta']['result_count'] == 0:
        return permalinks

    for t in query_response['data']:
        author_id = t['author_id']
        username = get_username(author_id)
        if username in excludes_users:
            continue
        permalinks.append('https://twitter.com/' + username + '/status/' + t['id'])
    return permalinks

def run():
    connect_to_endpoint()
