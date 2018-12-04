import json
from models.DB import DB


class NeverHaveIEverQueston(object):
    def __init__(self, question_id, question):
        self.id = int(question_id)
        self.question = question

    @classmethod
    def get_by_id(cls, question_id):
        result = DB().fetch_one('SELECT * FROM `nhie_questions` WHERE id=?', [int(question_id)])
        question_id, question = result
        return cls(question_id, question)

    @classmethod
    def get_all(cls):
        results = DB().fetch_all('SELECT * FROM `nhie_questions`')
        questions = [cls(question_id, question) for question_id, question in results]
        return questions


if __name__ == '__main__':
    questions_list = NeverHaveIEverQueston.get_all()
    print (json.dumps([nq.__dict__ for nq in questions_list]))
    pass
