import requests
import json
import datetime
import re
import html
import os
import time

from pathlib import Path
from config import CONFIG
from config import ProgLangDict
from config import BASE_URL
from config import HEADERS
from config import PROXIES
from config import COOKIE_PATH
from config import SOLUTION_FOLDER
from config import SOLUTION_FOLDER_NAME
from config import MAX_DIGIT_LEN
from config import CONTENT
from quiz import QuizItem
from utils import rep_unicode_in_code
from utils import check_and_make_dir
from selenium import webdriver
from collections import OrderedDict, Iterable
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Leetcode:

    def __init__(self):
        self.items = []
        self.submissions = []
        self.num_solved = 0
        self.num_total = 0
        self.num_lock = 0
        # change proglang to list
        # config set multi languages
        self.languages = [x.strip() for x in CONFIG['language'].split(',')]
        proglangs = [
            ProgLangDict[x.strip()] for x in CONFIG['language'].split(',')
        ]
        self.prolangdict = dict(zip(self.languages, proglangs))
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.proxies = PROXIES
        self.cookies = None

    def login(self):
        LOGIN_URL = self.base_url + '/accounts/login/'  # NOQA
        if not CONFIG['username'] or not CONFIG['password']:
            raise Exception(
                'Leetcode - Please input your username and password in config.cfg.'
            )

        usr = CONFIG['username']
        pwd = CONFIG['password']
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--disable-gpu')
        executable_path = CONFIG.get('driverpath')
        driver = webdriver.Chrome(
            chrome_options=options, executable_path=executable_path
        )
        driver.get(LOGIN_URL)

        login = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "login")))
        password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        buttons = driver.find_elements_by_tag_name('button')
        login.send_keys(usr)
        password.send_keys(pwd)
        time.sleep(2)
        for button in buttons:
            if button.text == "登录" or button.text == "Sign In":
                driver.execute_script("arguments[0].click();", button)
                break
        # driver.find_element_by_name('login').send_keys(usr)
        # driver.find_element_by_name('password').send_keys(pwd)
        # driver.find_element_by_id('id_remember').click()
        # btns = driver.find_elements_by_tag_name('button')
        # print(btns)
        # submit_btn = btns[0]
        # submit_btn.click()

        time.sleep(3)
        webdriver_cookies = driver.get_cookies()
        driver.close()
        if 'LEETCODE_SESSION' not in [
            cookie['name'] for cookie in webdriver_cookies
        ]:
            raise Exception('Please check your config or your network.')

        with open(COOKIE_PATH, 'w') as f:
            json.dump(webdriver_cookies, f, indent=2)
        self.cookies = {
            str(cookie['name']): str(cookie['value'])
            for cookie in webdriver_cookies
        }
        self.session.cookies.update(self.cookies)

    def load_items_from_api(self):
        """ load items from api"""
        api_url = self.base_url + '/api/problems/algorithms/'  # NOQA

        r = self.session.get(api_url, proxies=PROXIES)
        assert r.status_code == 200
        rst = json.loads(r.text)
        # make sure your user_name is not None
        # thus the stat_status_pairs is real
        if not rst['user_name']:
            raise Exception("Something wrong with your personal info.\n")

        self.items = []  # destroy first ; for sake maybe needn't
        self.num_solved = rst['num_solved']
        self.num_total = rst['num_total']
        self.items = list(self._generate_items_from_api(rst))
        self.num_lock = len([i for i in self.items if i.is_lock])
        self.items.reverse()

    def load(self):
        """
        load: all in one
        login -> load api -> load submissions -> solutions to items
        return `all in one items`
        """
        # if cookie is valid, get api_url twice
        # TODO: here can optimize
        if not self.is_login:
            self.login()
        self.load_items_from_api()
        self.load_submissions()
        self.load_solutions_to_items()

    def _generate_items_from_api(self, json_data):
        stat_status_pairs = json_data['stat_status_pairs']
        for quiz in stat_status_pairs:
            if quiz['stat']['question__hide']:
                continue

            data = {}
            data['question__title_slug'] = quiz['stat']['question__title_slug']
            data['question__title'] = quiz['stat']['question__title']
            data['question__article__slug'] = quiz['stat'][
                'question__article__slug'
            ]
            # data['is_paid'] = json_data['is_paid']
            data['paid_only'] = quiz['paid_only']
            data['level'] = quiz['difficulty']['level']
            data['is_favor'] = quiz['is_favor']
            data['total_acs'] = quiz['stat']['total_acs']
            data['total_submitted'] = quiz['stat']['total_submitted']
            data['question_id'] = quiz['stat']['question_id']
            data['status'] = quiz['status']
            item = QuizItem(**data)
            yield item

    @property
    def is_login(self):
        """ validate if the cookie exists and not overtime """
        api_url = self.base_url + '/api/problems/algorithms/'  # NOQA
        if not COOKIE_PATH.exists():
            return False

        with open(COOKIE_PATH, 'r') as f:
            webdriver_cookies = json.load(f)
        self.cookies = {
            str(cookie['name']): str(cookie['value'])
            for cookie in webdriver_cookies
        }
        self.session.cookies.update(self.cookies)
        r = self.session.get(api_url, proxies=PROXIES)
        if r.status_code != 200:
            return False

        data = json.loads(r.text)
        return 'user_name' in data and data['user_name'] != ''

    def load_submissions(self):
        """ load all submissions from leetcode """
        # set limit a big num
        print('Please wait ...')
        limit = 20
        offset = 0
        last_key = ''
        while True:
            print('try to load submissions from ', offset, ' to ', offset + limit)
            submissions_url = '{}/api/submissions/?format=json&limit={}&offset={}&last_key={}'.format(
                self.base_url, limit, offset, last_key
            )

            resp = self.session.get(submissions_url, proxies=PROXIES)
            # print(submissions_url, ':', resp.status_code)
            assert resp.status_code == 200
            data = resp.json()
            if 'has_next' not in data.keys():
                raise Exception('Get submissions wrong, Check network\n')

            self.submissions += data['submissions_dump']
            if data['has_next']:
                offset += limit
                last_key = data['last_key']
                # print('last_key:', last_key)
                time.sleep(2.5)
            else:
                break

    def load_solutions_to_items(self):
        """
        load all solutions to items
        combine submission's `runtime` `title` `lang` `submission_url` to items
        """
        titles = [i.question__title for i in self.items]
        itemdict = OrderedDict(zip(titles, self.items))

        def make_sub(sub):
            return dict(
                runtime=int(sub['runtime'][:-3]),
                title=sub['title'],
                lang=sub['lang'],
                submission_url=self.base_url + sub['url'],
            )

        ac_subs = [
            make_sub(sub)
            for sub in self.submissions
            if sub['status_display'] == 'Accepted'
        ]

        def remain_shortesttime_submissions(submissions):
            submissions_dict = {}
            for item in submissions:
                k = '{}-{}'.format(item['lang'], item['title'])
                if k not in submissions_dict.keys():
                    submissions_dict[k] = item
                else:
                    old = submissions_dict[k]
                    if item['runtime'] < old['runtime']:
                        submissions_dict[k] = item
            return list(submissions_dict.values())

        shortest_subs = remain_shortesttime_submissions(ac_subs)
        for solution in shortest_subs:
            title = solution['title']
            if title in itemdict.keys():
                itemdict[title].solutions.append(solution)

    def _get_code_by_solution(self, solution):
        """
        get code by solution
        solution: type dict
        """
        solution_url = solution['submission_url']
        # print(solution_url)
        r = self.session.get(solution_url, proxies=PROXIES)
        assert r.status_code == 200
        pattern = re.compile(
            r'<meta name=\"description\" content=\"(?P<question>.*)\" />\n    \n    <meta property=\"og:image\"',
            re.S,
        )
        m1 = pattern.search(r.text)
        question = m1.groupdict()['question'] if m1 else None
        if not question:
            raise Exception(
                'Can not find question descript in question:{title}'.format(
                    title=solution['title']
                )
            )

        # html.unescape to remove &quot; &#39;
        question = html.unescape(question)
        pattern = re.compile(
            r'submissionCode: \'(?P<code>.*)\',\n  editCodeUrl', re.S
        )
        m1 = pattern.search(r.text)
        code = m1.groupdict()['code'] if m1 else None
        if not code:
            raise Exception(
                'Can not find solution code in question:{title}'.format(
                    title=solution['title']
                )
            )

        code = rep_unicode_in_code(code)
        return question, code

    def _get_code_with_anno(self, solution):
        question, code = self._get_code_by_solution(solution)
        language = solution['lang']
        # generate question with anno
        lines = []
        for line in question.split('\n'):
            if line.strip() == '':
                lines.append(self.prolangdict[language].annotation)
            else:
                lines.append(
                    '{anno} {line}'.format(
                        anno=self.prolangdict[language].annotation,
                        line=html.unescape(line),
                    )
                )
        quote_question = '\n'.join(lines)
        # generate content
        content = '# -*- coding:utf-8 -*-' + '\n' * 3 if language == 'python' else ''
        content += quote_question
        content += '\n' * 3
        content += code
        content += '\n'
        return content

    def _download_code_by_quiz(self, quiz):
        """
        Download code by quiz
        quiz: type QuizItem
        """
        qid = quiz.question_id
        qtitle = quiz.question__title_slug
        slts = list(
            filter(lambda i: i['lang'] in self.languages, quiz.solutions)
        )
        if not slts:
            print(
                'No solution with the set languages in question:{}-{}'.format(
                    qid, qtitle
                )
            )
            return

        qname = '{id}-{title}'.format(id=str(qid).zfill(int(MAX_DIGIT_LEN)), title=qtitle)
        print('begin download ' + qname)
        path = Path.joinpath(SOLUTION_FOLDER, qname)
        check_and_make_dir(path)
        for slt in slts:
            fname = '{title}.{ext}'.format(
                title=qtitle, ext=self.prolangdict[slt['lang']].ext
            )
            filename = Path.joinpath(path, fname)
            content = self._get_code_with_anno(slt)
            import codecs

            with codecs.open(filename, 'w', 'utf-8') as f:
                print('write to file ->', fname)
                f.write(content)

    def _find_item_by_quiz_id(self, qid):
        """
        find the item by quiz id
        """
        lst = list(filter(lambda x: x.question_id == qid, self.items))
        if len(lst) == 1:
            return lst[0]

        print('No exits quiz id:', qid)

    def download_by_id(self, qid):
        quiz = self._find_item_by_quiz_id(qid)
        if quiz:
            self._download_code_by_quiz(quiz)

    def download(self):
        """ download all solutions with single thread """
        ac_items = [i for i in self.items if i.is_pass]
        for quiz in ac_items:
            # time.sleep(1)
            self._download_code_by_quiz(quiz)

    def download_with_thread_pool(self, workers):
        """ download all solutions with multi thread """
        ac_items = [i for i in self.items if i.is_pass]
        from concurrent.futures import ThreadPoolExecutor

        pool = ThreadPoolExecutor(max_workers=workers)
        for quiz in ac_items:
            pool.submit(self._download_code_by_quiz, quiz)
        pool.shutdown(wait=True)

    def write_readme(self):
        """Write Readme to current folder"""
        languages_readme = ','.join([x.capitalize() for x in self.languages])
        md = '''# Leetcode Solutions with {language}
Update time:  {tm}
Auto created by [leetcode_generate](https://github.com/ygowill/leetcode)
I have solved **{num_solved}   /   {num_total}** problems
while there are **{num_lock}** problems still locked.
(Notes: :lock: means you need to buy a book from Leetcode to unlock the problem)

| id | Title | Source Code | Article | Difficulty
|:---:|:---:|:---:|:---:|:---:|'''.format(
            language=languages_readme,
            tm=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            num_solved=self.num_solved,
            num_total=self.num_total,
            num_lock=self.num_lock,
            repo=CONFIG['repo'],
        )
        md += '\n'
        for item in self.items:
            if CONTENT != 'all' and item.status != CONTENT:
                continue
            article = '&nbsp;'
            if item.question__article__slug:
                article = '[:memo:](https://leetcode.com/articles/{article}/)'.format(
                    article=item.question__article__slug
                )
            if item.is_lock:
                language = ':lock:'
            else:
                if item.solutions:
                    dirname = '{folder}/{id}-{title}'.format(
                        folder=SOLUTION_FOLDER_NAME,
                        id=str(item.question_id).zfill(int(MAX_DIGIT_LEN)),
                        title=item.question__title_slug,
                    )
                    language = '&nbsp;'
                    language_lst = [
                        i['lang']
                        for i in item.solutions
                        if i['lang'] in self.languages
                    ]
                    while language_lst:
                        lan = language_lst.pop()
                        language += '[{language}]({repo}/blob/master/{dirname}/{title}.{ext})'.format(
                            language=lan.capitalize(),
                            repo=CONFIG['repo'],
                            dirname=dirname,
                            title=item.question__title_slug,
                            ext=self.prolangdict[lan].ext,
                        )
                        language += ' '
                else:
                    language = '&nbsp;'
            language = language.strip()
            md += '|{id}|[{title}]({url})|{language}|{article}|{difficulty}|\n'.format(
                id=item.question_id,
                title=item.question__title_slug,
                url=item.url,
                language=language,
                article=article,
                difficulty=item.difficulty,
            )
        with open('README.md', 'w') as f:
            f.write(md)

    def push_to_github(self):
        strdate = datetime.datetime.now().strftime('%Y-%m-%d')
        cmd_git_add = 'git add .'
        cmd_git_commit = 'git commit -m "update at {date}"'.format(
            date=strdate
        )
        cmd_git_push = 'git push -u origin master'
        os.system(cmd_git_add)
        os.system(cmd_git_commit)
        os.system(cmd_git_push)
