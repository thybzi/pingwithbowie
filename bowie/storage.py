"""Storage routines"""
from bowie import config
import redis

WORDS_LIST_KEY = 'words'
PREV_COLLECTION_LIST_KEY = 'prev'
RECENT_COLLECTION_LIST_KEY = 'recent'
UPCOMING_COLLECTION_LIST_KEY = 'upcoming'


def get_conn():
    """Establish connection and return redis instance"""
    # Get redis config
    try:
        cfg = config.get('redis')
    except BaseException as ex:
        raise Exception('Cannot get redis configuration: %s' % ex)

    # Establish connection
    try:
        rds = redis.StrictRedis(**cfg)
    except BaseException as ex:
        raise Exception('Cannot establish redis connection: %s' % ex)

    # Return redis instance
    return rds


def get_members(key):
    """Wrapper method for getting all members of specified list

    Args:
        key (str) Name of redis list
    """
    # Connect to redis
    try:
        rds = get_conn()
    except BaseException as ex:
        raise Exception('Cannot connect to redis: %s' % ex)

    # Get members of the list
    try:
        members = rds.lrange(key, 0, -1)
    except BaseException as ex:
        raise Exception('Cannot get `%s` list from redis: %s' % (key, ex))

    # Return obtained words
    return members


def get_words():
    """Get words list from storage"""
    # Get words list
    try:
        words = get_members(WORDS_LIST_KEY)
    except BaseException as ex:
        raise Exception('Cannot get words list: %s' % ex)

    # Return obtained words
    return words


def get_prev_collection():
    """Get previous collection list from storage"""
    # Get collection items
    try:
        collection = get_members(PREV_COLLECTION_LIST_KEY)
    except BaseException as ex:
        raise Exception('Cannot get previous collection: %s' % ex)

        # Return obtained collection items
    return collection


def get_recent_collection():
    """Get recent collection list from storage"""
    # Get collection items
    try:
        collection = get_members(RECENT_COLLECTION_LIST_KEY)
    except BaseException as ex:
        raise Exception('Cannot get recent collection: %s' % ex)

    # Return obtained collection items
    return collection


def set_words(words):
    """Store given words to redis, replacing previous list

    Args:
        words (list of string) or (list of unicode)
    """
    # Connect to redis
    try:
        rds = get_conn()
    except BaseException as ex:
        raise Exception('Cannot connect to redis: %s' % ex)

    # Remove previous list members
    try:
        rds.delete(WORDS_LIST_KEY)
    except BaseException as ex:
        raise Exception('Cannot clear previous words list in redis: %s' % ex)

    # Write new words list to redis
    try:
        rds.rpush(WORDS_LIST_KEY, *words)
    except BaseException as ex:
        raise Exception('Cannot write new words list to redis: %s' % ex)


def shift_collections():
    """Replace "recent" collection with "upcoming" one, and "prev" collection with former "recent" one"""
    # Connect to redis
    try:
        rds = get_conn()
    except BaseException as ex:
        raise Exception('Cannot connect to redis: %s' % ex)

    # Overwrite "prev" collection with f"recent" one
    try:
        rds.rename(RECENT_COLLECTION_LIST_KEY, PREV_COLLECTION_LIST_KEY)
    except:
        pass  # That's not an error, because on the first step "recent" collection may not exist

    # Overwrite "recent" collection with "upcoming" one
    try:
        rds.rename(UPCOMING_COLLECTION_LIST_KEY, RECENT_COLLECTION_LIST_KEY)
    except BaseException as ex:
        raise Exception('Cannot overwrite recent collection: %s' % ex)


def append_upcoming_item(item):
    """Add new item to upcoming collection

    Args:
        item (str) Stringified JSON data representing tweet
    """
    # Connect to redis
    try:
        rds = get_conn()
    except BaseException as ex:
        raise Exception('Cannot connect to redis: %s' % ex)

    # Write item to redis
    try:
        rds.rpush(UPCOMING_COLLECTION_LIST_KEY, item)
    except BaseException as ex:
        raise Exception('Cannot write new upcoming item to redis: %s' % ex)


def clear_upcoming_collection():
    """Remove all members from upcoming collection"""
    # Connect to redis
    try:
        rds = get_conn()
    except BaseException as ex:
        raise Exception('Cannot connect to redis: %s' % ex)

    # Clear upcoming collection list
    try:
        rds.delete(UPCOMING_COLLECTION_LIST_KEY)
    except BaseException as ex:
        raise Exception('Cannot clear upcoming collection in redis: %s' % ex)
