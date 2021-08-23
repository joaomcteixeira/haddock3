"""
In-house implementation of toml config files for HADDOCK3.

It does not implement all features of TOML files, but it does implement
the features needed for HADDOCK3. What config reader parses:

* Accepts repeated keys.
  * Repetitions get `.#` suffixes, where `#` is integer
* Allows in-line comments
* lists can be defined in multilines (comments are allowed)
  * multi-line lists must be followed by an empty line.
* Values must be parseable by:
  * `ast.literal_eval`
  * `datetime.fromisoformat`
"""
import ast
import re
from datetime import datetime


# string separator for internal reasons
# intents to be a string that will never happen in the config
INTERNAL_SEP = '_dnkljkqwdkjwql_'

# line regexes
# https://regex101.com/r/jZ8Rw7/1
header_re = re.compile(r'^ *\[([^\[\]].*?)\]')

# https://regex101.com/r/BNf7O5/1
string_re = re.compile(r'''^ *(\w+) *= *[\"\'](.*?)[\"\']''')

# https://regex101.com/r/G2tfE8/1
number_re = re.compile(r'^ *(\w+) *= *(\d+\.?\d+)\s')

# https://regex101.com/r/FBJFFt/1
list_one_liner_re = re.compile(r'^ *(\w+) *= *(\[.*\])')

# https://regex101.com/r/aAmXao/1
list_multiliner_re = re.compile(r" *(\w+) *= *\[\ *#?[^\]\n]*$")

# https://regex101.com/r/yhU3do/1
true_re = re.compile(r'^ *(\w+) *= *([tT]rue)')
false_re = re.compile(r'^ *(\w+) *= *([fF]alse)')


class NoGroupFoundError(Exception):
    pass


def read_config(f):
    """Parse HADDOCK3 config file to a dictionary."""
    d = {}

    # main keys always come before any subdictionary
    d1 = d

    # fin can't be processed to a list at this stage
    # it must be kept as a generator
    fin = open(f)

    pure_lines = filter(_is_correct_line, map(_process_line, fin))
    key = None
    for line in pure_lines:
        print(line)

        # treats header
        header_group = header_re.match(line)
        if header_group:
            key = header_group[1]
            if key in d:
                _num = str(sum(1 for _k in d if _k.startswith(key)))
                key += INTERNAL_SEP + _num

            d1 = d.setdefault(key, {})
            continue

        # evals if key:value are defined in a single line
        try:
            key, value = get_one_line_group(line)
        except NoGroupFoundError:
            pass
        else:
            d1[key] = value
            continue

        # evals if key:value is defined in multiple lines
        mll_group = list_multiliner_re.match(line)

        if mll_group:
            key = mll_group[1]
            idx = line.find('[')
            # need to send `fin` and not `pure_lines`
            block = line[idx:] + _get_list_block(fin)
            list_ = _eval_list_str(block)
            d1[key] = list_
            continue

        # if the flow reaches here...
        raise ValueError(f'Can\'t process this line: {line!r}')

    fin.close()
    return _make_nested_keys(d)


def _is_correct_line(line):
    return not _is_comment(line)


def _is_comment(line):
    """Assert if line is a comment or a line to ignore."""
    is_comment = \
        line.startswith('#') \
        or not bool(line)

    return is_comment


def _process_line(line):
    return line.strip()


def _replace_bool(s):
    "Replace booleans and try to parse."""
    s = s.replace('true', 'True')
    s = s.replace('false', 'False')
    return s


def _eval_list_str(s):
    """Evaluates a string to a list."""
    s = '[' + s.strip(',[]') + ']'
    s = _replace_bool(s)
    return ast.literal_eval(s)


def get_one_line_group(line):
    """Attempt to identify a key:value pair in a single line."""
    for method, func in regex_single_line_methods:
        group = method.match(line)
        # return first found
        if group:
            return group[1], ast.literal_eval(group[2])

    # all regex-based methods have failed
    # now try methods not based on regex
    try:
        key, value = (s.strip() for s in line.split('='))
    except ValueError:
        raise NoGroupFoundError('Line does not match any group.')

    for method in regex_single_line_special_methods:
        try:
            return key, method(value)
        except Exception:
            continue

    raise NoGroupFoundError('Line does not match any group.')


def _get_list_block(fin):
    """
    Concatenates a list in a string from a multiline list.

    Considers that a list ends when an empty line is found.
    """
    block = []
    for line in fin:

        line = _process_line(line)
        if line.startswith('#'):
            continue

        if not line:
            break

        block.append(line)

    return ''.join(block).strip()


def _make_nested_keys(d):
    """
    Converts dotted nested keys into actual nested keys.

    Example
    -------
    {"one.two": {'foo': 'bar'}}
    {"one": {"two": {'foo': 'bar'}}}

    {"one.two": {...}, "one.foo": {...}}
    {"one": {"two": {...}}, {"foo": {...}}}
    """
    d1 = {}

    for key, value in d.items():

        if isinstance(value, dict):

            keys = [_k.replace(INTERNAL_SEP, '.') for _k in key.split('.')]
            dk = d1.setdefault(keys[0], {})

            for k in keys[1:]:
                dk = dk.setdefault(k, {})

            dk.update(value)

        else:
            d1[key] = value

    return d1


def get_module_name(name):
    """Gets the name according to the config parser."""
    return name.split('.')[0]


# methods to parse single line values
# (regex, func)
regex_single_line_methods = [
    (string_re, ast.literal_eval),
    (number_re, ast.literal_eval),
    (list_one_liner_re, _eval_list_str),
    (true_re, lambda x: True),
    (false_re, lambda x: False),
    ]

regex_single_line_special_methods = [
    datetime.fromisoformat,
    ]
