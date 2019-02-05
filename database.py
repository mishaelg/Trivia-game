from abc import ABC, abstractmethod


class Database(ABC):
    """
    Abstract class to all databases
    """
    def draw_questions(self, num, category, diff):
        """
        Draw questions from internet source
        :param num: number of question
        :param category: category of question
        :param diff: question difficulty
        :return: questions in jason format
        """
        pass

    def add_questions(self, questions):
        """
        Loads questions into the database
        :param df: dataframe of all the questions
        """
        pass

    def add_user(self, user):
        """
        Adds a user to the database
        :param user: string username
        """
        pass

    def get_categories(self):
        """
        Gets all the possible categories in the database
        :return: list of all the category names
        """
        pass
