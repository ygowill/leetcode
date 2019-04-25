from config import BASE_URL


class QuizItem:
    """ QuizItem """
    base_url = BASE_URL

    def __init__(self, **data):
        self.__dict__.update(data)
        self.solutions = []

    def __str__(self):
        return '<Quiz: {question_id}-{question__title_slug}({difficulty})-{is_pass}>'.format(
            question_id=self.question_id,
            question__title_slug=self.question__title_slug,
            difficulty=self.difficulty,
            is_pass=self.is_pass,
        )

    def __repr__(self):
        return self.__str__()

    @property
    def json_object(self):
        addition_properties = [
            'is_pass', 'difficulty', 'is_lock', 'url', 'acceptance'
        ]
        dct = self.__dict__
        for prop in addition_properties:
            dct[prop] = getattr(self, prop)
        return dct

    @property
    def is_pass(self):
        return True if self.status == 'ac' else False

    @property
    def difficulty(self):
        difficulty = {1: "Easy", 2: "Medium", 3: "Hard"}
        return difficulty[self.level]

    @property
    def is_lock(self):
        return not self.is_favor and self.paid_only

    @property
    def url(self):
        return '{base_url}/problems/{question__title_slug}'.format(
            base_url=self.base_url,
            question__title_slug=self.question__title_slug,
        )

    @property
    def acceptance(self):
        return '%.1f%%' % (
                float(self.total_acs) * 100 / float(self.total_submitted)
        )