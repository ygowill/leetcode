import configparser
from pathlib import Path
from collections import namedtuple


def get_user_config_from_file():
    cp = configparser.ConfigParser()
    cp.read(CONFIG_FILE)
    if 'leetcode' not in list(cp.sections()):
        raise Exception('tag [leetcode] not exist! please check yor leetcode.conf')

    username = cp.get('leetcode', 'username')
    password = cp.get('leetcode', 'password')
    if not username or not password:  # username and password not none
        raise Exception(
            'Please configure your username and password in leetcode.conf.'
        )

    language = cp.get('leetcode', 'language')
    if not language:
        raise Exception('Please configure you language in leetcode.conf')

    repo = cp.get('leetcode', 'repo')
    if not repo:
        raise Exception('Please configure your Github repo address in leetcode.conf')

    driverpath = cp.get('leetcode', 'driverpath')
    if not repo:
        raise Exception('Please configure your dirver path in leetcode.conf')
    rst = dict(
        username=username,
        password=password,
        language=language.lower(),
        repo=repo,
        driverpath=driverpath,
    )
    return rst


def get_path_config_from_file():
    cp = configparser.ConfigParser()
    cp.read(CONFIG_FILE)
    if 'solution' not in list(cp.sections()):
        raise Exception('tag [solution] not exist! please check yor leetcode.conf')
    if 'url' not in list(cp.sections()):
        raise Exception('tag [url] not exist! please check yor leetcode.conf')

    solution_folder_name = cp.get('solution', 'solution_folder_name')
    if not solution_folder_name:
        raise Exception('Please configure your solution folder name in leetcode.conf')

    max_digit_len = cp.get('solution', 'max_digit_len')
    if not max_digit_len:
        raise Exception('Please configure your max_digit_len in leetcode.conf')

    base_url = cp.get('url', 'base_url')
    if not base_url:
        raise Exception('Please configure your base url in leetcode.conf')

    rst = dict(
        folder_name=solution_folder_name,
        max_digit_len=max_digit_len,
        base_url=base_url
    )
    return rst


HOME = Path.cwd()
CONFIG_FILE = 'leetcode.conf'
CONFIG = get_user_config_from_file()
PATHCONFIG = get_path_config_from_file()

MAX_DIGIT_LEN = PATHCONFIG['max_digit_len']
SOLUTION_FOLDER_NAME = PATHCONFIG['folder_name']
SOLUTION_FOLDER = Path.joinpath(HOME, SOLUTION_FOLDER_NAME)
COOKIE_PATH = Path.joinpath(HOME, 'cookies.json')
BASE_URL = PATHCONFIG['base_url']
# If you have proxy, change PROXIES below
PROXIES = None
HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'leetcode.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36',
    # NOQA
}

ProgLang = namedtuple('ProgLang', ['language', 'ext', 'annotation'])
ProgLangList = [
    ProgLang('cpp', 'cpp', '//'),
    ProgLang('java', 'java', '//'),
    ProgLang('python', 'py', '#'),
    ProgLang('python3', 'py', '#'),
    ProgLang('c', 'c', '//'),
    ProgLang('csharp', 'cs', '//'),
    ProgLang('javascript', 'js', '//'),
    ProgLang('ruby', 'rb', '#'),
    ProgLang('kotlin', 'kt', '//'),
    ProgLang('swift', 'swift', '//'),
    ProgLang('golang', 'go', '//'),
    ProgLang('scala', 'scala', '//'),
    ProgLang('rust', 'rs', '//'),
]
ProgLangDict = dict((item.language, item) for item in ProgLangList)
