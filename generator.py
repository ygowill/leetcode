import sys
import sched
import time

from leetcode import Leetcode

schedule = sched.scheduler(time.time, time.sleep)


def do_job(lc):
    lc.load()
    print('Leetcode load self info')
    if len(sys.argv) == 1:
        # simple download
        # leetcode.dowload()
        # we use multi thread
        print('download all leetcode solutions')
        # leetcode.download_with_thread_pool()
        lc.download()
    else:
        for qid in sys.argv[1:]:
            print('begin leetcode by id: {id}'.format(id=qid))
            lc.download_by_id(int(qid))
    print('Leetcode finish dowload')
    lc.write_readme()
    print('Leetcode finish write readme')
    # lc.push_to_github()
    print('push to github')


if __name__ == '__main__':
    lc = Leetcode()
    schedule.enter(0, 0, do_job, (lc,))
    schedule.run()
