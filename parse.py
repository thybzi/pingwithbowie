"""Command line tool to parse text into words and store it to redis, replacing any previously saved words set

Example:
    python add.py <filename>
"""
from bowie import storage
from bowie import txtools
import sys
import io


def prompt_if_is_correct(filename, words_count):
    """Prompt user if file content is parsed correctly

    Args:
        filename (str): Input file name and path
        words_count (int): Number of words in the text

    Returns:
        (boolean) True if user confirmed results, False otherwise

    Todo:
        Use global scope vars instead of function args?
    """
    print('File processed: %s, contains %d words' % (filename, words_count))
    action = raw_input('Use these words as collection base? (Y/n) ').lower()
    if action in ['y', 'yes', '']:
        return True
    elif action in ['n', 'no']:
        return False
    else:
        print('Please answer "y" or "n".\n')
        return prompt_if_is_correct(filename, words_count)


# Get filename
try:
    filename = sys.argv[1]
except:
    print('Usage: python parse.py <filename>\n')
    sys.exit(100)

# Read file content
try:
    with io.open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
except:
    print('Cannot read file: %s; aborting.\n' % filename)
    sys.exit(200)

# Parse file content into components
try:
    words = txtools.split_to_words(content)
except:
    print('Cannot parse contents of file: %s; aborting.\n' % filename)
    sys.exit(201)

# Prompt user if results are correct
if not prompt_if_is_correct(filename, len(words)):
    print('Aborted by user.\n')
    sys.exit(101)

# Save text item to database
try:
    storage.set_words(words)
except BaseException as ex:
    print('Storage error while saving words list: %s; aborting.\n' % ex)
    sys.exit(301)

# Report success
print('\n====================')
print('New words list stored successfully')
print('====================\n')
