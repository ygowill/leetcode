import re
from pathlib import Path


def rep_unicode_in_code(code):
    """
    Replace unicode to str in the code
    like '\u003D' to '='
    :param code: type str
    :return: type str
    """
    pattern = re.compile('(\\\\u[0-9a-zA-Z]{4})')
    m = pattern.findall(code)
    for item in set(m):
        code = code.replace(item, chr(int(item[2:], 16)))  # item[2:]去掉\u
    return code


def check_and_make_dir(dirname):
    p = Path(dirname)
    if not p.exists():
        p.mkdir(parents=True)
