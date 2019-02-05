from database import Database
import pandas as pd
from pymongo import MongoClient
import numpy as np


class Mongo(Database):
    def draw_questions(self, num, category, diff):
        """
        Draw questions from internet source
        :param num: number of question
        :param category: category of question
        :param diff: question difficulty
        :return: questions in jason format
        """
        client = MongoClient()
        db = client.Trivia_game_db
        questions = db.questions
        draws = questions.aggregate([{"$match": {"category": category, "difficulty": diff}}, {"$sample": {"size": num}}])
        return draws

    def add_questions(self, df):
        """
        Loads questions into the database
        :param df: dataframe of all the questions
        """
        client = MongoClient()
        db = client.Trivia_game_db
        questions = db.questions
        for question in df.to_dict('records'):
            self.add_category(question['category'])
            questions.update({"question": question['question']}, question, upsert=True)

    def add_user(self, user):
        """
        Adds a user to the database
        :param user: string username
        """
        client = MongoClient()
        db = client.Trivia_game_db
        users = db.users
        users.update({"username": user}, {"username": user}, upsert=True)

    def get_categories(self):
        """
        Gets all the possible categories in the database
        :return: list of all the category names
        """
        client = MongoClient()
        db = client.Trivia_game_db
        categories = db.categories
        results = categories.find()
        categories_list = [doc['category'] for doc in results]
        return categories_list

    def get_categories_with_diff(self):
        client = MongoClient()
        db = client.Trivia_game_db
        questions = db.questions
        result = questions.aggregate(
            [

                {"$group": {"_id": {"CategoryName": "$category", "Difficulty": "$difficulty"}}}
            ]
        )
        final_list = [elem['_id'] for elem in list(result)]
        return pd.DataFrame(list(final_list))

    def add_category(self, category_name):
        client = MongoClient()
        db = client.Trivia_game_db
        categories = db.categories
        categories.update({"category": category_name}, {"category": category_name}, upsert=True)

    def remove_category(self, category_id):
        client = MongoClient()
        db = client.Trivia_game_db
        questions = db.questions
        categories = db.categories
        questions.deleteMany({'category': category_id})
        categories.deleteMany({'category': category_id})

    def add_admin_question(self, question):
        client = MongoClient()
        db = client.Trivia_game_db
        questions = db.questions
        questions.update({"question": question['question']}, question, upsert=True)

    def update_answers(self, username, text, answers):
        client = MongoClient()
        db = client.Trivia_game_db
        questions = db.questions
        for i in range(len(answers)):
            if answers[i] == 1:
                questions.update(
                    {"question": text[i]},
                    {
                        "$addToSet": {"correct_users": username}
                    }
                )
                questions.update(
                    {"question": text[i]},
                    {
                        "$pull": {"incorrect_users": username}
                    }
                )
            else:
                questions.update(
                    {"question": text[i]},
                    {
                        "$addToSet": {"incorrect_users": username}
                    }
                )
                questions.update(
                    {"question": text[i]},
                    {
                        "$pull": {"correct_users": username}
                    }
                )

    def get_categories_stats(self):
        client = MongoClient()
        db = client.Trivia_game_db
        questions = db.questions
        df_correct = pd.DataFrame(list(questions.aggregate([{"$unwind": "$correct_users"},
                                                            {"$group": {"_id": "$category", "correct": {"$sum": 1}}}
                                                            ])))
        df_incorrect = pd.DataFrame(list(questions.aggregate([{"$unwind": "$incorrect_users"},
                                                              {"$group": {"_id": "$category", "incorrect": {"$sum": 1}}}
                                                              ])))
        df_total = df_correct.merge(df_incorrect)
        df_total.set_index('_id', inplace=True)
        df_total.index.name = 'Categories names'
        return df_total

    def get_diff_stats(self):
        client = MongoClient()
        db = client.Trivia_game_db
        questions = db.questions
        df_correct = pd.DataFrame(list(questions.aggregate([{"$unwind": "$correct_users"},
                                                            {"$group": {"_id": "$difficulty", "correct": {"$sum": 1}}}
                                                            ])))
        df_incorrect = pd.DataFrame(list(questions.aggregate([{"$unwind": "$incorrect_users"},
                                                              {"$group": {"_id": "$difficulty",
                                                                          "incorrect": {"$sum": 1}}}
                                                              ])))
        df_total = df_correct.merge(df_incorrect)
        df_total.set_index('_id', inplace=True)
        df_total.index.name = 'Difficulty'
        return df_total

    def get_winners(self):
        client = MongoClient()
        db = client.Trivia_game_db
        questions = db.questions
        df_correct = pd.DataFrame(list(questions.aggregate([{"$unwind": "$correct_users"},
                                                            {"$group": {"_id": "$correct_users",
                                                                        "correct": {"$sum": 1}}},
                                                            {"$sort": {"correct": -1}},
                                                            {"$limit": 3}
                                                            ])))
        df_incorrect = pd.DataFrame(list(questions.aggregate([{"$unwind": "$incorrect_users"},
                                                              {"$group": {"_id": "$incorrect_users",
                                                                          "incorrect": {"$sum": 1}}},
                                                              {"$match": {
                                                                  "_id": {"$in": list(df_correct['_id'].values)}}},
                                                              {"$sort": {"incorrect": 1}}
                                                              ])))
        df_total = df_correct.merge(df_incorrect)
        df_total.rename(columns={'_id': 'Username'}, inplace=True)
        return df_total


