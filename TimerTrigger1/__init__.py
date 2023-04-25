import os
import logging
import json
from datetime import datetime, timezone, timedelta
import azure.functions as func

VERSION = '2.0-rc4'

import slack
slack_token = os.getenv("SLACK_TOKEN")
slack_channel_id = os.getenv("SLACK_CHANNEL_ID")
slack_client = slack.WebClient(slack_token)

from shared_code import AzureBlobStorage as storage
storage.table_name = 'TwitterEgoSearch'
storage.account_name = os.getenv("TABLE_STORAGE_NAME")
storage.account_key = os.getenv("TABLE_STORAGE_KEY")

from shared_code import TwitterSearchRecent as tsr
tsr.bearer_token = os.getenv("BEARER_TOKEN")
nr_max_results = os.getenv("NR_MAX_RESULTS", default=10)


def main(myeventtimer: func.TimerRequest) -> None:
    logging.basicConfig(level=logging.DEBUG)
    logging.info(f'twitter ego-searching function v{VERSION}')
    logging.info('Search for the period from {} to {}'.format(
        (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(timespec='seconds').replace('+00:00', 'Z'),
         datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')))

    # Twitter Search
    excludes_users = storage.get_values_from('FilterUser')
    search_keywords = storage.get_values_from('Keyword')
    tsr.query_params['query'] = 'lang:ja -is:retweet'
    for key in search_keywords:
        tsr.append_query_keyword(f'"{key}"')
    tsr.query_params['start_time'] = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(timespec='seconds').replace('+00:00', 'Z')
    tsr.query_params['max_results'] = nr_max_results
    logging.info(f'{json.dumps(tsr.query_params, indent=2)}')

    tsr.run()
    permalinks = tsr.get_permalinks(excludes_users=excludes_users)

    # Twitter Timeline
    search_timeline = storage.get_values_from('Timeline')
    tsr.query_params['query'] = '-is:retweet'
    for key in search_timeline:
        tsr.append_query_keyword(f'from:{key}')
    logging.info(f'{json.dumps(tsr.query_params, indent=2)}')

    tsr.run()
    permalinks += tsr.get_permalinks()

    # Slack send
    for link in set(permalinks):
        logging.info(f'Permalink: {link}')
        slack_client.chat_postMessage(channel=slack_channel_id, text=link)
