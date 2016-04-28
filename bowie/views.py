"""Flash views for JSON API commands"""
from bowie import app
from bowie import storage
from bowie import twitter
import json
import calendar


@app.route('/api/collections/')
def collected():
    """Return data for previous and recent tweet collections

    Example:
        /api/collections/?rnd=1454885884221
    """

    # Get words list
    try:
        words = storage.get_words()
    except:
        return api_error('Storage error when getting words list', 301)

    # Get recent collection
    try:
        recent_data = storage.get_recent_collection()
    except:
        recent_data = []

    # Get prev collection
    try:
        prev_data = storage.get_prev_collection()
    except:
        prev_data = []

    result = {
        'recent': [],
        'prev': [],
    }

    # List tweets data
    for key, data in {'recent': recent_data, 'prev': prev_data}.items():

        for i, item in enumerate(data):

            # Parse tweet data
            try:
                tweet_data = json.loads(item)
            except:
                return api_error('Tweet data error', 400)

            # Build tweet URL
            try:
                tweet_url = twitter.get_tweet_url(tweet_data)
            except:
                return api_error('Tweet data error', 401)

            # Get tweet author screen name
            try:
                tweet_author = tweet_data['user']['screen_name']
            except:
                return api_error('Tweet data error', 402)

            # Parse and format tweet time
            try:
                tweet_time_struct = twitter.parse_twitter_time(tweet_data['created_at'])
                tweet_timestamp = int(calendar.timegm(tweet_time_struct))
                tweet_time = twitter.get_formatted_datetime(tweet_time_struct)
            except:
                return api_error('Tweet data error', 403)

            # Get tweet text
            try:
                tweet_content = tweet_data['text']
            except:
                return api_error('Tweet data error', 404)

            # Append item to results list
            result[key].append({
                'word': words[i],
                'tweet_url': tweet_url,
                'tweet_author': tweet_author,
                'tweet_time': tweet_time,
                'tweet_timestamp': tweet_timestamp,
                'tweet_content': tweet_content,
            })

    # Output JSON results
    try:
        return json.dumps(result)
    except:
        return api_error('Result output error', 500)


def api_error(error_message, error_code, http_code=500):
    """Output error JSON for API command

    Args:
        error_message (str): Human-readable error message
        error_code (int): Error code for more convenient debugging
        http_code (int=500): HTTP status code (e.g. 404 or 500)
    """
    output = {
        'error': error_message,
        'code': error_code,
    }
    return json.dumps(output), http_code
