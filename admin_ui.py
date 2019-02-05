from ui import UI
import pandas as pd


class AdminUI(UI):
    """
    The interface on which the options will be displayed, this class is for console
    """
    def show_menu(self, categories):
        """

        :param categories: all the possible categories right now in the databbase
        :return: the option the admin has chosen
        """
        diff_levels = ['easy', 'medium', 'hard']
        q_type_opts = ['multi', 'bool']
        print("Hello admin, welcome to the admin menu!")
        print("Please select what would you like to do:")
        while(True):
            x = int(input("1 for add or remove a category, 2 to add a Trivia \nquestion, 3 to load question into the database, 4 and for game \nstatistics and 5 to quit: "))
            if x == 1:
                return self.option1(categories)
            elif x == 2:
                return self.option2(categories, q_type_opts, diff_levels)
            elif x == 3:
                return [3]
            elif x == 4:
                x = int(input("Enter 1 for bar plot of correct/incorrect answers per category,\n2 for bar plot of correct/incorrect answers per difficulty, or 3 for the highscore table: "))
                return [4, x]
            elif x == 5:
                exit()

    def option1(self, categories):
        """
        This function is to add or remove a category
        :param categories: list of possible categories in the database right now
        """
        while (True):
            x = int(input("Enter 1 to add a category, 2 to remove and 0 to quit: "))
            if x == 1:
                category = input("Enter category name: ")
                return [1, 1, category]  # add category
            elif x == 2:
                print(categories)
                category_num = int(input("Enter the number corresponding to the category name you would like to choose: "))
                return [1, 2, categories[category_num - 1]]  # remove category
            elif x == 0:
                exit(0)
            else:
                print("Invalid input")

    def option2(self, categories, q_type_opts, diff_levels):
        """
        get a new question from admin and shape it in a jason format
        :param categories: list of possible categories in the database right now
        :param q_type_opts: list of all the question type to choose from : True/ false or multi answer
        :param diff_levels: list of all the possible diff levels to choose from
        :return: the new question in a jason format
        """
        print(categories)
        while (True):
            category_num = int(input("Enter the number corresponding to the category name you would like to choose: "))
            if category_num not in list(range(len(categories))):
                print("Invalid input")
            else:
                q_type = int(input("Choose the type of question, 0 for multiple choice, 1 for True/False: "))
                q_type = q_type_opts[q_type]
                diff = int(input("Enter difficulty level: 0 for easy, 1 for medium, 2 for hard: "))
                question = input("Enter question:")
                if q_type == 'multi':
                    opt1 = input("Enter the real answer: ")
                    opt2 = input("Enter fake answer: ")
                    opt3 = input("Enter fake answer: ")
                    opt4 = input("Enter fake answer: ")
                    return [2, {'category': categories[category_num - 1], 'correct_answer': opt1, 'difficulty': diff_levels[diff],
                                'incorrect_answers': [opt2, opt3, opt4], 'question': question, 'type': 'multiple'}]
                if q_type == 'bool;':
                    opt1 = input("Enter True / False: ")
                    return [2,
                            {'category': categories[category_num - 1], 'correct_answer': opt1, 'difficulty': diff_levels[diff],
                             'incorrect_answers': ['Doesnt matter'], 'question': question, 'type': 'boolean'}]

    def option3(self, categories):
        """

        :param categories:
        :return:
        """
        diff_levels = ['easy', 'medium', 'hard']
        num = int(input("Enter the number of questions: "))
        diff = int(input("Enter difficulty level: 0 for easy, 1 for medium, 2 for hard: "))
        print(categories)
        while(True):
            category_num = int(input("Enter the category you would like to draw from: "))
            if category_num in list(range(1, len(categories) + 1)):
                return [categories[category_num], num, diff_levels[diff]]

    def plot_bar(self, df):
        df.plot.bar();

    def show_winners(self, winners):
        print(winners)