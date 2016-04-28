"""Text parsing and processing tools"""
import re


def split_to_words(text, include_positions=False):
    """Split provided text into words
    Adapted from: http://stackoverflow.com/a/22075070 (see also `word_chars` below)

    Args:
        text (str or unicode): Input text
        include_positions (bool=False): Extend return format with words' first letter positions (see examples below)

    Returns:
        (list of str) or (list of unicode) or (list of dict): Format depends on value of `include_position` argument

    Examples:
        from twiwri import txtools
        text = 'Foo, bar... Qux?'
        txtools.split_words(text)        # -> ['Foo', 'bar', 'Qux']
        txtools.split_words(text, True)  # -> [{'content': 'Foo', 'position': 0},
                                         #     {'content': 'bar', 'position': 5},
                                         #     {'content': 'Qux', 'position': 12}]

    Todo:
        Return tuples (not dicts) when include_positions=True?
    """
    result = []
    for match in re.finditer(word_chars + '+', text, re.UNICODE):
        if include_positions:
            result.append({
               'content': match.group(0),
               'position': match.start()
            })
        else:
            result.append(match.group(0))
    return result


def remove_diacritics(text):
    """Remove diacritic sign (accents) from provided text
    Adapted from: http://stackoverflow.com/a/18391901/3027390 (see also `diacritics_map` and `diacritics_list` below)

    Args:
        text (str): Input text

    Returns:
        str: Text with diacritic char replaced with correspondent ASCII ones

    Raises:
        Exception: Cannot build diacritics map
        Exception: Cannot do replace

    Todo:
        Too excessive replaced char range?
    """
    # Prepare diacritics map if empty
    if len(diacritics_map) == 0:
        try:
            for item in diacritics_list:
                for letter in item[1]:
                    diacritics_map[letter] = item[0]
        except Exception as ex:
            raise Exception('Cannot build diacritics map: %s' % ex)

    # Replace callback for re.sub
    def choose(match):
        char = match.group(0)
        if char in diacritics_map:
            return diacritics_map[char]
        else:
            return char

    # Do the replace
    try:
        result = re.sub(ur'[^\u0000-\u007E]', choose, text, re.UNICODE)
    except Exception as ex:
        raise Exception('Cannot do replace: %s' % ex)

    return result


# Characters used in words
# In our terms, number is also a "word" (i.e. the phrase "It is 40000 km long" contains 5 words)
# Words also can contain digits (i.e. "20ft" and "i18n" are words)
# Apostrophe is treated as letter (part of the word: "It's", "don`t" etc.)
# Hyphen is treated as word-breaker for now (i.e. the phrase "It's bed-time" contains 3 words: "It's", "bed", "time")
word_chars = \
    ur'[0-9\'`\u2019\u02BC' \
    ur'\u0041-\u005A\u0061-\u007A\u00AA\u00B5\u00BA\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02C1\u02C6-\u02D1' \
    ur'\u02E0-\u02E4\u02EC\u02EE\u0370-\u0374\u0376\u0377\u037A-\u037D\u0386\u0388-\u038A\u038C\u038E-\u03A1' \
    ur'\u03A3-\u03F5\u03F7-\u0481\u048A-\u0527\u0531-\u0556\u0559\u0561-\u0587\u05D0-\u05EA\u05F0-\u05F2\u0620-\u064A' \
    ur'\u066E\u066F\u0671-\u06D3\u06D5\u06E5\u06E6\u06EE\u06EF\u06FA-\u06FC\u06FF\u0710\u0712-\u072F\u074D-\u07A5' \
    ur'\u07B1\u07CA-\u07EA\u07F4\u07F5\u07FA\u0800-\u0815\u081A\u0824\u0828\u0840-\u0858\u08A0\u08A2-\u08AC' \
    ur'\u0904-\u0939\u093D\u0950\u0958-\u0961\u0971-\u0977\u0979-\u097F\u0985-\u098C\u098F\u0990\u0993-\u09A8' \
    ur'\u09AA-\u09B0\u09B2\u09B6-\u09B9\u09BD\u09CE\u09DC\u09DD\u09DF-\u09E1\u09F0\u09F1\u0A05-\u0A0A\u0A0F\u0A10' \
    ur'\u0A13-\u0A28\u0A2A-\u0A30\u0A32\u0A33\u0A35\u0A36\u0A38\u0A39\u0A59-\u0A5C\u0A5E\u0A72-\u0A74\u0A85-\u0A8D' \
    ur'\u0A8F-\u0A91\u0A93-\u0AA8\u0AAA-\u0AB0\u0AB2\u0AB3\u0AB5-\u0AB9\u0ABD\u0AD0\u0AE0\u0AE1\u0B05-\u0B0C\u0B0F' \
    ur'\u0B10\u0B13-\u0B28\u0B2A-\u0B30\u0B32\u0B33\u0B35-\u0B39\u0B3D\u0B5C\u0B5D\u0B5F-\u0B61\u0B71\u0B83' \
    ur'\u0B85-\u0B8A\u0B8E-\u0B90\u0B92-\u0B95\u0B99\u0B9A\u0B9C\u0B9E\u0B9F\u0BA3\u0BA4\u0BA8-\u0BAA\u0BAE-\u0BB9' \
    ur'\u0BD0\u0C05-\u0C0C\u0C0E-\u0C10\u0C12-\u0C28\u0C2A-\u0C33\u0C35-\u0C39\u0C3D\u0C58\u0C59\u0C60\u0C61' \
    ur'\u0C85-\u0C8C\u0C8E-\u0C90\u0C92-\u0CA8\u0CAA-\u0CB3\u0CB5-\u0CB9\u0CBD\u0CDE\u0CE0\u0CE1\u0CF1\u0CF2' \
    ur'\u0D05-\u0D0C\u0D0E-\u0D10\u0D12-\u0D3A\u0D3D\u0D4E\u0D60\u0D61\u0D7A-\u0D7F\u0D85-\u0D96\u0D9A-\u0DB1' \
    ur'\u0DB3-\u0DBB\u0DBD\u0DC0-\u0DC6\u0E01-\u0E30\u0E32\u0E33\u0E40-\u0E46\u0E81\u0E82\u0E84\u0E87\u0E88\u0E8A' \
    ur'\u0E8D\u0E94-\u0E97\u0E99-\u0E9F\u0EA1-\u0EA3\u0EA5\u0EA7\u0EAA\u0EAB\u0EAD-\u0EB0\u0EB2\u0EB3\u0EBD' \
    ur'\u0EC0-\u0EC4\u0EC6\u0EDC-\u0EDF\u0F00\u0F40-\u0F47\u0F49-\u0F6C\u0F88-\u0F8C\u1000-\u102A\u103F\u1050-\u1055' \
    ur'\u105A-\u105D\u1061\u1065\u1066\u106E-\u1070\u1075-\u1081\u108E\u10A0-\u10C5\u10C7\u10CD\u10D0-\u10FA' \
    ur'\u10FC-\u1248\u124A-\u124D\u1250-\u1256\u1258\u125A-\u125D\u1260-\u1288\u128A-\u128D\u1290-\u12B0\u12B2-\u12B5' \
    ur'\u12B8-\u12BE\u12C0\u12C2-\u12C5\u12C8-\u12D6\u12D8-\u1310\u1312-\u1315\u1318-\u135A\u1380-\u138F\u13A0-\u13F4' \
    ur'\u1401-\u166C\u166F-\u167F\u1681-\u169A\u16A0-\u16EA\u1700-\u170C\u170E-\u1711\u1720-\u1731\u1740-\u1751' \
    ur'\u1760-\u176C\u176E-\u1770\u1780-\u17B3\u17D7\u17DC\u1820-\u1877\u1880-\u18A8\u18AA\u18B0-\u18F5\u1900-\u191C' \
    ur'\u1950-\u196D\u1970-\u1974\u1980-\u19AB\u19C1-\u19C7\u1A00-\u1A16\u1A20-\u1A54\u1AA7\u1B05-\u1B33\u1B45-\u1B4B' \
    ur'\u1B83-\u1BA0\u1BAE\u1BAF\u1BBA-\u1BE5\u1C00-\u1C23\u1C4D-\u1C4F\u1C5A-\u1C7D\u1CE9-\u1CEC\u1CEE-\u1CF1\u1CF5' \
    ur'\u1CF6\u1D00-\u1DBF\u1E00-\u1F15\u1F18-\u1F1D\u1F20-\u1F45\u1F48-\u1F4D\u1F50-\u1F57\u1F59\u1F5B\u1F5D' \
    ur'\u1F5F-\u1F7D\u1F80-\u1FB4\u1FB6-\u1FBC\u1FBE\u1FC2-\u1FC4\u1FC6-\u1FCC\u1FD0-\u1FD3\u1FD6-\u1FDB\u1FE0-\u1FEC' \
    ur'\u1FF2-\u1FF4\u1FF6-\u1FFC\u2071\u207F\u2090-\u209C\u2102\u2107\u210A-\u2113\u2115\u2119-\u211D\u2124\u2126' \
    ur'\u2128\u212A-\u212D\u212F-\u2139\u213C-\u213F\u2145-\u2149\u214E\u2183\u2184\u2C00-\u2C2E\u2C30-\u2C5E' \
    ur'\u2C60-\u2CE4\u2CEB-\u2CEE\u2CF2\u2CF3\u2D00-\u2D25\u2D27\u2D2D\u2D30-\u2D67\u2D6F\u2D80-\u2D96\u2DA0-\u2DA6' \
    ur'\u2DA8-\u2DAE\u2DB0-\u2DB6\u2DB8-\u2DBE\u2DC0-\u2DC6\u2DC8-\u2DCE\u2DD0-\u2DD6\u2DD8-\u2DDE\u2E2F\u3005\u3006' \
    ur'\u3031-\u3035\u303B\u303C\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FC-\u30FF\u3105-\u312D\u3131-\u318E' \
    ur'\u31A0-\u31BA\u31F0-\u31FF\u3400-\u4DB5\u4E00-\u9FCC\uA000-\uA48C\uA4D0-\uA4FD\uA500-\uA60C\uA610-\uA61F\uA62A' \
    ur'\uA62B\uA640-\uA66E\uA67F-\uA697\uA6A0-\uA6E5\uA717-\uA71F\uA722-\uA788\uA78B-\uA78E\uA790-\uA793\uA7A0-\uA7AA' \
    ur'\uA7F8-\uA801\uA803-\uA805\uA807-\uA80A\uA80C-\uA822\uA840-\uA873\uA882-\uA8B3\uA8F2-\uA8F7\uA8FB\uA90A-\uA925' \
    ur'\uA930-\uA946\uA960-\uA97C\uA984-\uA9B2\uA9CF\uAA00-\uAA28\uAA40-\uAA42\uAA44-\uAA4B\uAA60-\uAA76\uAA7A' \
    ur'\uAA80-\uAAAF\uAAB1\uAAB5\uAAB6\uAAB9-\uAABD\uAAC0\uAAC2\uAADB-\uAADD\uAAE0-\uAAEA\uAAF2-\uAAF4\uAB01-\uAB06' \
    ur'\uAB09-\uAB0E\uAB11-\uAB16\uAB20-\uAB26\uAB28-\uAB2E\uABC0-\uABE2\uAC00-\uD7A3\uD7B0-\uD7C6\uD7CB-\uD7FB' \
    ur'\uF900-\uFA6D\uFA70-\uFAD9\uFB00-\uFB06\uFB13-\uFB17\uFB1D\uFB1F-\uFB28\uFB2A-\uFB36\uFB38-\uFB3C\uFB3E\uFB40' \
    ur'\uFB41\uFB43\uFB44\uFB46-\uFBB1\uFBD3-\uFD3D\uFD50-\uFD8F\uFD92-\uFDC7\uFDF0-\uFDFB\uFE70-\uFE74\uFE76-\uFEFC' \
    ur'\uFF21-\uFF3A\uFF41-\uFF5A\uFF66-\uFFBE\uFFC2-\uFFC7\uFFCA-\uFFCF\uFFD2-\uFFD7\uFFDA-\uFFDC]'


# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
diacritics_map = {}
"""(dict of str: str): Map for diacritic symbols replacements
   Used in `remove_diacritics()`, being built on its first call (on the basis of `diacritics_list` tuple list)
   Format: {u'\u0041': 'A',
            u'\u24B6': 'A',
            ...
            u'\u0042': 'B',
            ...
            u'\u004F': 'O',
            ...}
"""
diacritics_list = [
    ('A',  ur'\u0041\u24B6\uFF21\u00C0\u00C1\u00C2\u1EA6\u1EA4\u1EAA\u1EA8\u00C3\u0100\u0102\u1EB0\u1EAE\u1EB4\u1EB2'
           ur'\u0226\u01E0\u00C4\u01DE\u1EA2\u00C5\u01FA\u01CD\u0200\u0202\u1EA0\u1EAC\u1EB6\u1E00\u0104\u023A\u2C6F'),
    ('AA', ur'\uA732'),
    ('AE', ur'\u00C6\u01FC\u01E2'),
    ('AO', ur'\uA734'),
    ('AU', ur'\uA736'),
    ('AV', ur'\uA738\uA73A'),
    ('AY', ur'\uA73C'),
    ('B',  ur'\u0042\u24B7\uFF22\u1E02\u1E04\u1E06\u0243\u0182\u0181'),
    ('C',  ur'\u0043\u24B8\uFF23\u0106\u0108\u010A\u010C\u00C7\u1E08\u0187\u023B\uA73E'),
    ('D',  ur'\u0044\u24B9\uFF24\u1E0A\u010E\u1E0C\u1E10\u1E12\u1E0E\u0110\u018B\u018A\u0189\uA779'),
    ('DZ', ur'\u01F1\u01C4'),
    ('Dz', ur'\u01F2\u01C5'),
    ('E',  ur'\u0045\u24BA\uFF25\u00C8\u00C9\u00CA\u1EC0\u1EBE\u1EC4\u1EC2\u1EBC\u0112\u1E14\u1E16\u0114\u0116\u00CB'
           ur'\u1EBA\u011A\u0204\u0206\u1EB8\u1EC6\u0228\u1E1C\u0118\u1E18\u1E1A\u0190\u018E'),
    ('F',  ur'\u0046\u24BB\uFF26\u1E1E\u0191\uA77B'),
    ('G',  ur'\u0047\u24BC\uFF27\u01F4\u011C\u1E20\u011E\u0120\u01E6\u0122\u01E4\u0193\uA7A0\uA77D\uA77E'),
    ('H',  ur'\u0048\u24BD\uFF28\u0124\u1E22\u1E26\u021E\u1E24\u1E28\u1E2A\u0126\u2C67\u2C75\uA78D'),
    ('I',  ur'\u0049\u24BE\uFF29\u00CC\u00CD\u00CE\u0128\u012A\u012C\u0130\u00CF\u1E2E\u1EC8\u01CF\u0208\u020A\u1ECA'
           ur'\u012E\u1E2C\u0197'),
    ('J',  ur'\u004A\u24BF\uFF2A\u0134\u0248'),
    ('K',  ur'\u004B\u24C0\uFF2B\u1E30\u01E8\u1E32\u0136\u1E34\u0198\u2C69\uA740\uA742\uA744\uA7A2'),
    ('L',  ur'\u004C\u24C1\uFF2C\u013F\u0139\u013D\u1E36\u1E38\u013B\u1E3C\u1E3A\u0141\u023D\u2C62\u2C60\uA748\uA746'
           ur'\uA780'),
    ('LJ', ur'\u01C7'),
    ('Lj', ur'\u01C8'),
    ('M',  ur'\u004D\u24C2\uFF2D\u1E3E\u1E40\u1E42\u2C6E\u019C'),
    ('N',  ur'\u004E\u24C3\uFF2E\u01F8\u0143\u00D1\u1E44\u0147\u1E46\u0145\u1E4A\u1E48\u0220\u019D\uA790\uA7A4'),
    ('NJ', ur'\u01CA'),
    ('Nj', ur'\u01CB'),
    ('O',  ur'\u004F\u24C4\uFF2F\u00D2\u00D3\u00D4\u1ED2\u1ED0\u1ED6\u1ED4\u00D5\u1E4C\u022C\u1E4E\u014C\u1E50\u1E52'
           ur'\u014E\u022E\u0230\u00D6\u022A\u1ECE\u0150\u01D1\u020C\u020E\u01A0\u1EDC\u1EDA\u1EE0\u1EDE\u1EE2\u1ECC'
           ur'\u1ED8\u01EA\u01EC\u00D8\u01FE\u0186\u019F\uA74A\uA74C'),
    ('OI', ur'\u01A2'),
    ('OO', ur'\uA74E'),
    ('OU', ur'\u0222'),
    ('OE', ur'\u008C\u0152'),
    ('oe', ur'\u009C\u0153'),
    ('P',  ur'\u0050\u24C5\uFF30\u1E54\u1E56\u01A4\u2C63\uA750\uA752\uA754'),
    ('Q',  ur'\u0051\u24C6\uFF31\uA756\uA758\u024A'),
    ('R',  ur'\u0052\u24C7\uFF32\u0154\u1E58\u0158\u0210\u0212\u1E5A\u1E5C\u0156\u1E5E\u024C\u2C64\uA75A\uA7A6\uA782'),
    ('S',  ur'\u0053\u24C8\uFF33\u1E9E\u015A\u1E64\u015C\u1E60\u0160\u1E66\u1E62\u1E68\u0218\u015E\u2C7E\uA7A8\uA784'),
    ('T',  ur'\u0054\u24C9\uFF34\u1E6A\u0164\u1E6C\u021A\u0162\u1E70\u1E6E\u0166\u01AC\u01AE\u023E\uA786'),
    ('TZ', ur'\uA728'),
    ('U',  ur'\u0055\u24CA\uFF35\u00D9\u00DA\u00DB\u0168\u1E78\u016A\u1E7A\u016C\u00DC\u01DB\u01D7\u01D5\u01D9\u1EE6'
           ur'\u016E\u0170\u01D3\u0214\u0216\u01AF\u1EEA\u1EE8\u1EEE\u1EEC\u1EF0\u1EE4\u1E72\u0172\u1E76\u1E74\u0244'),
    ('V',  ur'\u0056\u24CB\uFF36\u1E7C\u1E7E\u01B2\uA75E\u0245'),
    ('VY', ur'\uA760'),
    ('W',  ur'\u0057\u24CC\uFF37\u1E80\u1E82\u0174\u1E86\u1E84\u1E88\u2C72'),
    ('X',  ur'\u0058\u24CD\uFF38\u1E8A\u1E8C'),
    ('Y',  ur'\u0059\u24CE\uFF39\u1EF2\u00DD\u0176\u1EF8\u0232\u1E8E\u0178\u1EF6\u1EF4\u01B3\u024E\u1EFE'),
    ('Z',  ur'\u005A\u24CF\uFF3A\u0179\u1E90\u017B\u017D\u1E92\u1E94\u01B5\u0224\u2C7F\u2C6B\uA762'),
    ('a',  ur'\u0061\u24D0\uFF41\u1E9A\u00E0\u00E1\u00E2\u1EA7\u1EA5\u1EAB\u1EA9\u00E3\u0101\u0103\u1EB1\u1EAF\u1EB5'
           ur'\u1EB3\u0227\u01E1\u00E4\u01DF\u1EA3\u00E5\u01FB\u01CE\u0201\u0203\u1EA1\u1EAD\u1EB7\u1E01\u0105\u2C65'
           ur'\u0250'),
    ('aa', ur'\uA733'),
    ('ae', ur'\u00E6\u01FD\u01E3'),
    ('ao', ur'\uA735'),
    ('au', ur'\uA737'),
    ('av', ur'\uA739\uA73B'),
    ('ay', ur'\uA73D'),
    ('b',  ur'\u0062\u24D1\uFF42\u1E03\u1E05\u1E07\u0180\u0183\u0253'),
    ('c',  ur'\u0063\u24D2\uFF43\u0107\u0109\u010B\u010D\u00E7\u1E09\u0188\u023C\uA73F\u2184'),
    ('d',  ur'\u0064\u24D3\uFF44\u1E0B\u010F\u1E0D\u1E11\u1E13\u1E0F\u0111\u018C\u0256\u0257\uA77A'),
    ('dz', ur'\u01F3\u01C6'),
    ('e',  ur'\u0065\u24D4\uFF45\u00E8\u00E9\u00EA\u1EC1\u1EBF\u1EC5\u1EC3\u1EBD\u0113\u1E15\u1E17\u0115\u0117\u00EB'
           ur'\u1EBB\u011B\u0205\u0207\u1EB9\u1EC7\u0229\u1E1D\u0119\u1E19\u1E1B\u0247\u025B\u01DD'),
    ('f',  ur'\u0066\u24D5\uFF46\u1E1F\u0192\uA77C'),
    ('g',  ur'\u0067\u24D6\uFF47\u01F5\u011D\u1E21\u011F\u0121\u01E7\u0123\u01E5\u0260\uA7A1\u1D79\uA77F'),
    ('h',  ur'\u0068\u24D7\uFF48\u0125\u1E23\u1E27\u021F\u1E25\u1E29\u1E2B\u1E96\u0127\u2C68\u2C76\u0265'),
    ('hv', ur'\u0195'),
    ('i',  ur'\u0069\u24D8\uFF49\u00EC\u00ED\u00EE\u0129\u012B\u012D\u00EF\u1E2F\u1EC9\u01D0\u0209\u020B\u1ECB\u012F'
           ur'\u1E2D\u0268\u0131'),
    ('j',  ur'\u006A\u24D9\uFF4A\u0135\u01F0\u0249'),
    ('k',  ur'\u006B\u24DA\uFF4B\u1E31\u01E9\u1E33\u0137\u1E35\u0199\u2C6A\uA741\uA743\uA745\uA7A3'),
    ('l',  ur'\u006C\u24DB\uFF4C\u0140\u013A\u013E\u1E37\u1E39\u013C\u1E3D\u1E3B\u017F\u0142\u019A\u026B\u2C61\uA749'
           ur'\uA781\uA747'),
    ('lj', ur'\u01C9'),
    ('m',  ur'\u006D\u24DC\uFF4D\u1E3F\u1E41\u1E43\u0271\u026F'),
    ('n',  ur'\u006E\u24DD\uFF4E\u01F9\u0144\u00F1\u1E45\u0148\u1E47\u0146\u1E4B\u1E49\u019E\u0272\u0149\uA791\uA7A5'),
    ('nj', ur'\u01CC'),
    ('o',  ur'\u006F\u24DE\uFF4F\u00F2\u00F3\u00F4\u1ED3\u1ED1\u1ED7\u1ED5\u00F5\u1E4D\u022D\u1E4F\u014D\u1E51\u1E53'
           ur'\u014F\u022F\u0231\u00F6\u022B\u1ECF\u0151\u01D2\u020D\u020F\u01A1\u1EDD\u1EDB\u1EE1\u1EDF\u1EE3\u1ECD'
           ur'\u1ED9\u01EB\u01ED\u00F8\u01FF\u0254\uA74B\uA74D\u0275'),
    ('oi', ur'\u01A3'),
    ('ou', ur'\u0223'),
    ('oo', ur'\uA74F'),
    ('p',  ur'\u0070\u24DF\uFF50\u1E55\u1E57\u01A5\u1D7D\uA751\uA753\uA755'),
    ('q',  ur'\u0071\u24E0\uFF51\u024B\uA757\uA759'),
    ('r',  ur'\u0072\u24E1\uFF52\u0155\u1E59\u0159\u0211\u0213\u1E5B\u1E5D\u0157\u1E5F\u024D\u027D\uA75B\uA7A7\uA783'),
    ('s',  ur'\u0073\u24E2\uFF53\u00DF\u015B\u1E65\u015D\u1E61\u0161\u1E67\u1E63\u1E69\u0219\u015F\u023F\uA7A9\uA785'
           ur'\u1E9B'),
    ('t',  ur'\u0074\u24E3\uFF54\u1E6B\u1E97\u0165\u1E6D\u021B\u0163\u1E71\u1E6F\u0167\u01AD\u0288\u2C66\uA787'),
    ('tz', ur'\uA729'),
    ('u',  ur'\u0075\u24E4\uFF55\u00F9\u00FA\u00FB\u0169\u1E79\u016B\u1E7B\u016D\u00FC\u01DC\u01D8\u01D6\u01DA\u1EE7'
           ur'\u016F\u0171\u01D4\u0215\u0217\u01B0\u1EEB\u1EE9\u1EEF\u1EED\u1EF1\u1EE5\u1E73\u0173\u1E77\u1E75\u0289'),
    ('v',  ur'\u0076\u24E5\uFF56\u1E7D\u1E7F\u028B\uA75F\u028C'),
    ('vy', ur'\uA761'),
    ('w',  ur'\u0077\u24E6\uFF57\u1E81\u1E83\u0175\u1E87\u1E85\u1E98\u1E89\u2C73'),
    ('x',  ur'\u0078\u24E7\uFF58\u1E8B\u1E8D'),
    ('y',  ur'\u0079\u24E8\uFF59\u1EF3\u00FD\u0177\u1EF9\u0233\u1E8F\u00FF\u1EF7\u1E99\u1EF5\u01B4\u024F\u1EFF'),
    ('z',  ur'\u007A\u24E9\uFF5A\u017A\u1E91\u017C\u017E\u1E93\u1E95\u01B6\u0225\u0240\u2C6C\uA763'),
]
