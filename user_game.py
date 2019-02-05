from game import Game
from user_ui import UserUI
from sql import SQL
from mongo import Mongo


class UserGame(Game):
    def __init__(self, database):
        self.ui = UserUI
        self.db = eval(database)()

    def initiate_seq(self):
        categories = self.db.get_categories_with_diff()
        username, category, diff_level, q_num = self.ui.get_choices(categories, categories)
        self.db.add_user(username)
        while(True):
            try:
                answers, questions_id = self.ui.get_answers(self, self.db.draw_questions(q_num, category, diff_level))
                break
            except ConnectionError:
                self.ui.error_message(self)
                username, category, diff_level, q_num = self.ui.get_choices(categories, categories)

        self.db.update_answers(username, questions_id, answers)

