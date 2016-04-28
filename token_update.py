from bowie import config
from bowie import twitter


# Obtain twitter access token
try:
    token = twitter.get_token()
    print('\nTwitter token obtained:')
    print('=' * len(token))
    print(token)
    print('=' * len(token))
except BaseException as ex:
    raise Exception('Cannot obtain twitter access token: %s' % ex)

# Save token to config file
try:
    config.save_param('twitter', 'access_token', token)
    print('Token stored successfully (config file)')
except BaseException as ex:
    raise Exception('Cannot obtain new twitter access token: %s' % ex)
