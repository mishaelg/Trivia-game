from game import Game
from admin_ui import AdminUI
import pandas as pd
from sql import SQL
from mongo import Mongo
import requests
from requests.exceptions import ConnectionError


class AdminGame(Game):
    """
    manges all the actions that can be taken in admin mode
    """
    def __init__(self, database):
        """
        :param database: the data base the data will be stored in. possibilities are mongoDB or SQL
        """
        self.ui = AdminUI()
        self.db = eval(database)()

    def initiate_seq(self):
        """
        initiates the menu option for the admin, there are 4 options to choose from.
        """
        categories = self.db.get_categories()
        opt = self.ui.show_menu(categories)
        if opt[0] == 1:
            if opt[1] == 1:
                self.db.add_category(opt[2])
            elif opt[1] == 2:
                self.db.remove_category(opt[2])
        elif opt[0] == 2:
            question = opt[1]
            self.db.add_admin_question(question)
        elif opt[0] == 3:
            self.load_questions()
        elif opt[0] == 4:
            self.get_statistics(opt[1])

    def load_questions(self):
        """
        Loads a set of question from https://opentdb.com/api_category.php, according to the admin's choosing.
        """
        try:
            x = requests.get('https://opentdb.com/api_category.php')
        except ConnectionError as e:
            print(e)
            print("Website is currently down, try again later")
            exit(1)
        categories_dict = {elem['name']: elem['id'] for elem in x.json()['trivia_categories']}
        category, num, diff = self.ui.option3(list(categories_dict.keys()))
        self.db.add_category(category)
        questions = pd.DataFrame(pd.read_json(f'https://opentdb.com/api.php?amount={num}&category={categories_dict[category]}&difficulty={diff}').results.tolist())
        self.db.add_questions(questions)

    def get_statistics(self, opt):
        """
        :param opt: opt = 1 - show categorical statistics, opt = 2 - show statistic by difficulties, opt = 3 - show the winner of the game
        """
        if opt == 1:
            categories_stats = self.db.get_categories_stats()
            self.ui.plot_bar(categories_stats)
        elif opt == 2:
            diff_stats = self.db.get_diff_stats()
            self.ui.plot_bar(diff_stats)
        elif opt == 3:
            winners = self.db.get_winners()
            winners.index += 1
            self.ui.show_winners(winners)


