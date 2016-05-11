import sys
import io
import re
import json

# Get filename
try:
    filename = sys.argv[1]
except:
    print('Usage: python ass2json.py <filename>\n')
    sys.exit(100)

# Read file content
try:
    with io.open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
except:
    print('Cannot read file: %s; aborting.\n' % filename)
    sys.exit(200)

# Get needed lines
lines = filter(lambda x: x.startswith('Dialogue: '), content.splitlines())

# Build lyrics data
lyrics = []

# Each line corresponds the phrase
for line in lines:
    line_match = re.match(r'^Dialogue: 0,(\d):(\d\d):(\d\d\.\d\d),(\d):(\d\d):(\d\d\.\d\d),Default,,0,0,0,,(.+)$', line)
    if not line_match:
        continue
    begin_h, begin_m, begin_s, end_h, end_m, end_s, text = line_match.groups()
    begin = (int(begin_h) * 60 * 60) + (int(begin_m) * 60) + float(begin_s)
    end = (int(end_h) * 60 * 60) + (int(end_m) * 60) + float(end_s)

    # Fill the words data for the phrase
    words = []
    words_data = []
    word_begin = begin

    # Try to find all words by durations
    for word_match in re.finditer(r'\{\\k(\d+)\}([^{ ]*)', text):
        word_end = word_begin + (float(word_match.group(1)) / 100)
        word = word_match.group(2)
        if len(word):
            words.append(word)
            words_data.append({
                'enter': float("{0:.2f}".format(word_begin)),
                'leave': float("{0:.2f}".format(word_end)),
            })
        word_begin = word_end

    # If nothing found, consider to have a single word with full-phrase duration
    if not len(words):
        words.append(text)
        words_data.append({
            'enter': begin,
            'leave': end,
        })

    # Append phrase item
    lyrics.append({
        "phrase": ' '.join(words),
        "enter": begin,
        "leave": end,
        "words": words_data
    })

# Output result
print(json.dumps({"lyrics": lyrics}, indent=4, sort_keys=True))
