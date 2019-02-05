from ui import UI
import numpy as np
import pandas as pd
import html


class UserUI(UI):
    def get_choices(self, categories):
        print("Hello and welcome to a game of trivia!")
        user_name = input("Enter you username first: ")
        categories_list = list(set(categories['CategoryName'].values))
        print(categories_list)
        category_num = int(input("Enter the number of category corresponding to the \ncategory you would like to play: "))
        category = categories_list[category_num - 1]
        print("Those are the difficulty option for this category:")
        diff_levels = categories['Difficulty'][categories['CategoryName'] == category].values
        print(diff_levels)
        diff = int(input("Enter the difficulty level you would like to play at:"))
        num_of_questions = int(input("Enter the number of questions you would like to play: "))
        return user_name, category, diff_levels[diff - 1], num_of_questions

    def get_answers(self, questions):
        answers = []
        q_ids = []
        for question in questions:
            print("Your question is:", html.unescape(question['question']))
            if question['type'] == 'boolean':
                answer = int(input("Enter 0 for False, 1 for True: "))
                answer = 'True' if answer == 1 else 'False'
                answers.append(1 if answer == question['correct_answer'] else 0)
                try:
                    q_ids.append(question['question_id'])
                except KeyError:
                    q_ids.append(question['question'])
            else:
                print("Answers are: ")
                options = [question['correct_answer']] + question['incorrect_answers']
                np.random.shuffle(options)
                print(options)
                answer = int(input('Enter answer number, from 1 to 4: '))
                answers.append(1 if options[answer - 1] == question['correct_answer'] else 0)
                try:
                    q_ids.append(question['question_id'])
                except KeyError:
                    q_ids.append(question['question'])
        print(f"You were correct {sum(answers)} out of {len(answers)} times")
        print("Thanks for playing, goodbye!")
        return answers, q_ids

    def error_message(self):
        print("One of the parameters you have entered is invalid. Please try again")


