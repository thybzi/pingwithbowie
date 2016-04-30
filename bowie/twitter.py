"""Fetch, process and store tweets data"""
from bowie import config
from bowie import storage
from bowie import txtools
from twython import Twython
import re
import json
import threading
from Queue import Queue
import time


PRIORITY_HASHTAG = '#singwithbowie'
REQUEST_INTERVAL = 15 * 60 / 450
WORDS_PER_REQUEST = 3
VAIN_REQUESTS_UNTIL_FOCUS = 5
VAIN_HASHTAG_REQUESTS_MAX = 1
ITEMS_PER_REQUEST = 100


def get_token():
    """Get access token for Twitter OAuth 2.0

    Returns:
        str: Token string

    Raises:
        Exception: Cannot get twitter configuration
        Exception: Cannot get twitter access token
    """
    # Get config params
    try:
        cfg = config.get('twitter')
    except Exception as ex:
        raise Exception('Cannot get twitter configuration: %s' % ex)

    # Create API instance
    twitter = Twython(cfg['app_key'], cfg['app_secret'], oauth_version=2)

    # Obtain access token
    try:
        token = twitter.obtain_access_token()
    except Exception as ex:
        raise Exception('Cannot get twitter access token: %s' % ex)

    # Return obtained token
    return token


def get_api():
    """Get Twitter API instance

    Returns:
        twython.Twython

    Raises:
        Exception: Cannot get twitter configuration
    """
    try:
        cfg = config.get('twitter')
    except Exception as ex:
        raise Exception('Cannot get twitter configuration: %s' % ex)

    return Twython(cfg['app_key'], access_token=cfg['access_token'])


def assemble_collection():
    """Assemble the collection of sequential tweets forming the text"""

    def count_vain_request():
        """Increment counter for requests without any result, and reset productive requests counter
        Also disable priority hashtag mode if there were too many vain hashtag requests
        """
        request_counters['vain'] += 1
        request_counters['productive'] = 0
        if hashtag_mode['enabled'] and (request_counters['vain'] >= VAIN_HASHTAG_REQUESTS_MAX):
            hashtag_mode['enabled'] = False

    def count_productive_request():
        """Increment counter for requests having at least one result, and reset vain requests counter
        Also re-enable priority hashtag mode if it was disabled previously
        """
        request_counters['productive'] += 1
        request_counters['vain'] = 0
        if not hashtag_mode['enabled']:
            hashtag_mode['enabled'] = True

    def set_collected_words_count(count):
        """Store number of words found with last request

        Args:
            count (int)
        """
        request_counters['words_in_last'] = count
        if count:
            count_productive_request()
        else:
            count_vain_request()

    def is_hashtag_mode():
        """Report if priority hashtag mode should be enabled in the next request

        Returns:
            bool
        """
        return hashtag_mode['enabled']

    def is_focus_mode():
        """Report if focus mode should be enabled in the next request

        Returns:
            bool
        """
        return request_counters['vain'] >= VAIN_REQUESTS_UNTIL_FOCUS

    def get_searched_words():
        """Provide a list of words to be searched next
        Also provide a search query for twitter, optimized by excluding non-unique words

        Raises:
            KeyError: Cannot get primary search word
            KeyError: Cannot get secondary search word

        Returns:
            list of str: ['Three', 'unsearched', 'words']
            str: 'Three OR unsearched OR words'
        """
        def add_word(word):
            """Add word to `searched_words`
            Also add word to `query_words` if its normalized version is unique
            """
            searched_words.append(word)
            normalized = word.lower()
            if normalized not in query_words:
                query_words.append(normalized)

        # Prepare empty list for searched words
        searched_words = []
        query_words = []

        # Determine index of first unsearched word and store word's content
        index = last_word_data['index'] + 1
        try:
            add_word(words[index])
        except (IndexError, KeyError) as ex:
            raise KeyError('Cannot get primary search word: %s' % ex)

        # If focus mode is disabled, also list some following words to be searched for
        if not is_focus_mode():
            while (index < words_last_index) and (len(query_words) < WORDS_PER_REQUEST):
                index += 1
                try:
                    add_word(words[index])
                except (IndexError, KeyError) as ex:
                    raise KeyError('Cannot get secondary search word: %s' % ex)

        # Build search query for `q` twitter search param
        if is_hashtag_mode():
            query_words = map(lambda word: word + ' ' + PRIORITY_HASHTAG, query_words)
        query = ' OR '.join(query_words)

        # Return the list of words to be searched
        return searched_words, query

    def filter_older_posts(post):
        """Callback for filtering out the posts which are older than last collected one

        Args:
            post (dict): Tweet's parsed JSON data

        Todo:
            Check `post` format for necessary keys?
        """
        # If there is previously collected tweet, filter by tweet ID
        if last_word_data['tweet_id'] is not None:
            return post['id'] > last_word_data['tweet_id']
        # If no tweet previously collected, filter by tweet time
        else:
            return parse_twitter_time(post['created_at']) > last_word_data['time']

    def normalize_string(string):
        """Convert string to lowercase and remove diacritics

        Args:
            string (str): Input string
        """
        return txtools.remove_diacritics(string.lower())

    def fetch_next_results():
        """Fetch next tweet results from Twitter search

        Raises:
            ValueError: No words to search for
            Exception: Cannot fetch Twitter search results
            ValueError: Tweets data not found in search results
            Exception: Cannot normalize searched word
            Exception: Cannot remove usernames and hyperlinks from post text
            Exception: Cannot split post text into words
            Exception: Cannot normalize words from post text
            Exception: Cannot preprocess matching post data
            Exception: Cannot enqueue tweet data for saving to database

        Todo:
            Make real-time print reporting optional?
        """

        # Get next words to be searched
        searched_words, query = get_searched_words()
        if len(searched_words) < 1:
            raise ValueError('No words to search for')

        # Prepare search params
        params = {
            'q': query,
            'result_type': 'recent',
            'count': ITEMS_PER_REQUEST,
            'rnd': time.mktime(time.gmtime()),
        }
        if last_word_data['tweet_id'] is not None:
            params['since_id'] = last_word_data['tweet_id']

        # Report search query
        print('  ~ [%s] Searching for: %s' % (get_formatted_time(time.gmtime()), params['q']))

        # Initialize Twitter API instance
        twitter = get_api()

        # Get Twitter search results
        try:
            result = twitter.search(**params)
        except Exception as ex:
            raise Exception('Cannot fetch Twitter search results: %s' % ex)

        # Get posts data from result fetched
        try:
            # Reverse posts to have newest on top
            posts = reversed(result['statuses'])
        except Exception as ex:
            raise ValueError('Tweets data not found in search results: %s' % ex)

        # Collected words counter
        collected_words_count = 0

        # Cycle through searched words to determine which ones are found
        for word in searched_words:
            # Make word lowercase and remove diacritic signs (trying to emulate Twitter search approach within results)
            # TODO Investigate, check and possibly improve this emulation algorithm (may be unreliable for now)
            try:
                word_normalized = normalize_string(word)
            except Exception as ex:
                raise Exception('Cannot normalize searched word: %s' % ex)

            # Filter posts to remove ones older than last matched tweet (or older than assemble begin time)
            posts = filter(filter_older_posts, posts)

            # Cycle through posts to get the newest one that matches current word
            matching_post = None
            for post in posts:

                # Remove usernames and hyperlinks from post text
                try:
                    text_nolinks = re.sub(ur'(^|\s)(https://t\.co/\S+|@[a-zA-Z0-9_]+)', '', post['text'], re.UNICODE)
                except BaseException as ex:
                    raise Exception('Cannot remove usernames and hyperlinks from post text: %s' % ex)

                # Split post text into words
                try:
                    words_original = txtools.split_to_words(text_nolinks)
                except BaseException as ex:
                    raise Exception('Cannot split post text into words: %s' % ex)

                # Nothing to do if no words extracted
                if len(words_original) < 1:
                    continue

                # Convert extracted words to lowercase and remove diacritics
                try:
                    words_normalized = map(normalize_string, words_original)
                except Exception as ex:
                    raise Exception('Cannot normalize words from post text: %s' % ex)

                # If post's words contain searched word, this post is the match; stop further post cycling for this word
                if word_normalized in words_normalized:
                    matching_post = post
                    break

            # If matching post is found
            if matching_post is not None:

                # Prepare post data
                try:
                    collect_time_begin = last_word_data['collect_time_begin']
                    collect_time_end = time.gmtime()
                except Exception as ex:
                    raise Exception('Cannot preprocess matching post data: %s' % ex)

                # Enqueue data for database save
                try:
                    queue.put({
                        'tweet_data': json.dumps(matching_post),
                    })
                except Exception as ex:
                    raise Exception('Cannot enqueue tweet data for saving to database: %s' % ex)

                # Refresh last post data
                last_word_data['tweet_id'] = matching_post['id']
                last_word_data['time'] = parse_twitter_time(matching_post['created_at'])
                last_word_data['ordinal'] += 1
                last_word_data['index'] += 1
                last_word_data['collect_time_begin'] = collect_time_end

                # Count and report word collect success
                collected_words_count += 1
                collect_time_end_formatted = get_formatted_datetime(collect_time_end)
                print('[+] Collected word "%s" (%d of %d) at %s GMT' %
                      (word, last_word_data['ordinal'], words_count, collect_time_end_formatted))

            # If no matching post found for the word, skip all following searched words (otherwise sequence will break)
            else:
                break

        # Save results statistics
        set_collected_words_count(collected_words_count)

    def results_saver():
        """Worker that continuously reads enqueued tweet fetch results and saves them into database

        Raises:
            Exception: Cannot connect to database
            Exception: Database error when updating word entry
            Exception: Exactly 1 (one) word entry expected to be updated
            Exception: Database error when updating text entry
            Exception: Exactly 1 (one) text entry expected to be updated
            Exception: Database error when committing changes
        """
        while True:

            # Initialize `data` variable
            data = None

            # Catch any exception inside cycle to keep worker alive
            try:
                # Get next queued item
                data = queue.get()

                # If item is False, finish the process
                if not data:
                    exit(0)

                # Connect to database (new connection for each queue item to avoid connection timeouts)
                try:
                    storage.append_upcoming_item(data['tweet_data'])
                except Exception as ex:
                    raise Exception('Cannot append upcoming collection item: %s' % ex)

                queue.task_done()

            # If exception occurs, output error message and put fetched data back to queue
            # TODO Not the best way, because first queue item becomes last
            except Exception as ex:
                print('[ERROR!] %s' % ex)
                if data is not None:
                    queue.put(data)

    # Main process
    # TODO Move to separate method?

    # State process start time
    time_begin = time.gmtime()

    # Report process start
    print('\nAssembling new collection')
    print('Process started at %s GMT' % get_formatted_datetime(time_begin))

    # Get words list
    # TODO Get only uncollected words (to enable aborted process resume)?
    try:
        words = storage.get_words()
    except Exception as ex:
        raise Exception('Storage error when getting words list: %s' % ex)

    # Check words count
    words_count = len(words)
    if words_count < 1:
        raise Exception('No words to collect')

    # Thread-accessible storage for request statistics counters
    request_counters = {
        'productive': 0,
        'vain': 0,
        'words_in_last': 0,
    }

    # Thread-accessible value indicating whether priority hashtag mode is enabled
    hashtag_mode = {
        'enabled': True,
    }

    # Prepare initial data
    first_word_ordinal = 1
    last_word_data = {
        'index': -1,
        'ordinal': first_word_ordinal - 1,
        'time': time_begin,
        'tweet_id': None,
        'collect_time_begin': time_begin,
    }

    # Clear upcoming collection
    # TODO Only do that on forced restart
    try:
        storage.clear_upcoming_collection()
    except Exception as ex:
        raise Exception('Storage error when clearing upcoming collection: %s' % ex)

    # Initialize messages queue between fetchers and saver
    queue = Queue()

    # Invoke database saving worker
    saver = threading.Thread(target=results_saver)
    saver.daemon = True
    saver.start()

    # Invoke a new tweet fetcher at a given interval until all words are collected
    words_last_index = words_count - 1
    while last_word_data['index'] < words_last_index:
        fetch = threading.Thread(target=fetch_next_results)
        fetch.start()
        time.sleep(REQUEST_INTERVAL)
        fetch.join()  # TODO Need to terminate the fetcher at the end of interval -- does .join() really do the work?

    # After all words are collected, send a signal to stop the database worker and join its thread
    queue.put(False)
    saver.join()

    # Push upcoming collection as new "recent" collection
    try:
        storage.shift_collections()
    except Exception as ex:
        raise Exception('Storage error when shifting collections: %s' % ex)

    # State process finish time
    time_end = time.gmtime()

    # Report success
    print('\n====================')
    print('Assembled new collection')
    print('Process finished at %s GMT' % get_formatted_datetime(time_end))
    print('Collected %d words' % words_count)
    print('====================\n')


def convert_twitter_time(twitter_time):
    """Convert 'created_at' value of tweet into DATETIME format
    Taken from: http://stackoverflow.com/a/7711869

    Args:
        twitter_time (str): Time string in format: 'Wed Aug 27 13:08:45 +0000 2008'

    Returns:
        str: Time string in format: '2008-08-27 13:08:45'
    """
    return get_formatted_datetime(parse_twitter_time(twitter_time))


def parse_twitter_time(twitter_time):
    """Parse 'created_at' value of tweet into time structure object

    Args:
        twitter_time (str): Time string in format: 'Wed Aug 27 13:08:45 +0000 2008'

    Returns:
        time.struct_time: Time structure object
    """
    return time.strptime(twitter_time, '%a %b %d %H:%M:%S +0000 %Y')


def get_twitter_date(time_struct):
    """Get date formatted to use for 'since' Twitter search query param

    Args:
        time_struct (time.struct_time): Time structure object

    Returns:
        str: Date string in format: '2008-08-27'
    """
    return time.strftime('%Y-%m-%d', time_struct)


def get_formatted_datetime(time_struct):
    """Format time structure as readable datetime

    Args:
        time_struct (time.struct_time): Time structure object

    Returns:
        str: Time string in format: '2008-08-27 13:08:45'
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)


def get_formatted_time(time_struct):
    """Format time structure as readable time

    Args:
        time_struct (time.struct_time): Time structure object

    Returns:
        str: Time string in format: '13:08:45'
    """
    return time.strftime('%H:%M:%S', time_struct)


# Build tweet URL from tweet data
def get_tweet_url(tweet_data):
    return 'https://twitter.com/%s/status/%s' % (tweet_data['user']['screen_name'], tweet_data['id_str'])
