from database import Database
import pyodbc
import pandas as pd


class SQL(Database):
    def __init__(self):
        self.conn_string = "Driver={ODBC Driver 13 for SQL Server};" \
                      "Server=EXPERISDS7\SQLSERVER2017;" \
                      "Database=TriviaDB;" \
                      "Trusted_Connection=yes;"

    def draw_questions(self, num, category, diff):
        """
        Draw questions from internet source
        :param num: number of question
        :param category: category of question
        :param diff: question difficulty
        :return: questions in jason format
        """
        pass
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()
        category_id = self.get_category(category)
        sql_q = f"""
            SELECT TOP {num} *
            From Questions q 
            FULL OUTER JOIN QuestionsAnswers qa
            ON q.QuestionId = qa.QuestionsId
            WHERE CategoryId = {category_id} AND  Difficulty = '{diff}'
            ORDER BY NEWID()
            """
        rows = cursor.execute(sql_q).fetchall()
        questions = []
        for row in rows:
            if pd.isna(row.MultiQuestions):
                question = {'question_id': row.QuestionId, 'question': row.text, 'type': 'boolean'}
                if row.TrueorFalse == 0:
                    question['correct_answer'] = 'False'
                else:
                    question['correct_answer'] = 'True'
                questions.append(question)
            else:
                question = {'question_id': row.QuestionId, 'question': row.text,
                            'correct_answer': row.Opt1, 'incorrect_answers': [row.Opt2, row.Opt3, row.Opt4],
                            'type': 'multiple'}
                questions.append(question)
        return questions

    def add_questions(self, df):
        """
        Loads questions into the database
        :param df: dataframe of all the questions
        """
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()

        def f(row):
            sql_q = """
                        SELECT text
                        From Questions
                        WHERE text = ? 
                        """
            rows = cursor.execute(sql_q, row.question).fetchall()
            if len(rows) == 0:
                if row.type == 'boolean':
                    if row.correct_answer == 'True':
                        answer = 1
                    else:
                        answer = 0
                    sql_q = """
                            INSERT INTO  Questions                            
                            VALUES(?, ?, ?, NULL, ?) 
                            """
                    cursor.execute(sql_q, row.question, self.get_category(row.category), row.difficulty, answer)
                else:
                    sql_q = """
                                     INSERT INTO  Questions
                                     OUTPUT Inserted.QuestionId                            
                                     VALUES(?, ?, ?, NULL, NULL) 
                                     """
                    new_id = cursor.execute(sql_q, row.question, self.get_category(row.category), row.difficulty).fetchval()
                    self.add_answeropt(new_id, row.	correct_answer, row.incorrect_answers[0], row.incorrect_answers[1], row.incorrect_answers[2],)
                    sql_q = f"""
                             UPDATE Questions
                             SET MultiQuestions = {new_id}                          
                             WHERE QuestionId = {new_id} 
                             """
                    cursor.execute(sql_q)

        df.apply(f, axis=1)
        conn.commit()

    def add_user(self, user):
        """
        Adds a user to the database
        :param user: string username
        """
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()
        sql_q = """
                    IF NOT EXISTS (SELECT * FROM Users WHERE  Username = ?)

                    INSERT INTO Users(Username)
                    VALUES(?) 
                """
        cursor.execute(sql_q, user, user)
        conn.commit()

    def get_categories_with_diff(self):
        conn = pyodbc.connect(self.conn_string)
        sql_q = """
                SELECT DISTINCT c.CategoryName, q.Difficulty
                FROM Questions q JOIN Categories c
                ON q.CategoryId = c.CategoryId
                """
        categories = pd.read_sql(sql_q, conn)
        return categories

    def add_category(self, category_name):
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()
        sql_q = """
                        IF NOT EXISTS (SELECT * FROM Categories WHERE CategoryName = ?)
                        
                        INSERT INTO Categories( CategoryName)
                        VALUES(?)
                        
                                """
        cursor.execute(sql_q, category_name, category_name)
        conn.commit()

    def add_answeropt(self, question_id, opt1, opt2, opt3, opt4):
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()
        sql_q = """
                    SELECT DISTINCT QuestionsId
                    From QuestionsAnswers
                    WHERE QuestionsId = ?
                                        """
        rows = cursor.execute(sql_q, question_id).fetchall()
        if len(rows) == 1:
            return rows.QuestionId
        else:
            sql_q = """
                                INSERT INTO QuestionsAnswers
                                VALUES(?, ?, ?, ?, ?)
                                """
            cursor.execute(sql_q, question_id, opt1, opt2, opt3, opt4)
        conn.commit()

    def remove_category(self, category):
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()
        category_id = self.get_category(category)
        sql_q = """
                         SELECT QuestionId
                         FROM Questions
                         WHERE CategoryId = ?
                     """
        Ids = cursor.execute(sql_q, category_id).fetchall()
        Ids_list = tuple([elem[0] for elem in Ids])
        if len(Ids_list) > 0:
            sql_q = f"""
                               DELETE FROM UsersAnswers
                               WHERE QuestionId IN {Ids_list}
                            """
            cursor.execute(sql_q)
            sql_q = f"""
                               DELETE FROM QuestionsAnswers
                               WHERE QuestionsId IN {Ids_list}
                            """
            cursor.execute(sql_q)
        sql_q = """
                    DELETE FROM Questions
                    WHERE CategoryId = ?
                """
        cursor.execute(sql_q, category_id)
        sql_q = """
                    DELETE FROM Categories
                    WHERE CategoryId = ?
                """
        cursor.execute(sql_q, category_id)

        conn.commit()

    def add_admin_question(self, question):
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()
        category_id = self.get_category(question['category'])
        sql_q = """
                   SELECT *
                   FROM Questions
                   WHERE text = ?
               """
        rows = cursor.execute(sql_q, question['question']).fetchall()
        if len(rows) == 0:
            if question['type'] == 'bool':
                if question['correct_answer'] == 'True':
                    answer = 1
                else:
                    answer = 0
                sql_q = """
                        INSERT INTO  Questions                            
                        VALUES(?, ?, ?, NULL, ?) 
                        """
                cursor.execute(sql_q, question['question'], category_id, question['difficulty'], answer)
            else:
                sql_q = """
                                 INSERT INTO  Questions
                                 OUTPUT Inserted.QuestionId                            
                                 VALUES(?, ?, ?, NULL, NULL) 
                                 """
                new_id = cursor.execute(sql_q, question['question'], question['category'], question['difficulty']).fetchval()
                self.add_answeropt(new_id, question['correct_answer'], question['incorrect_answers'][0], question['incorrect_answers'][1],
                                   question['incorrect_answers'][2], )
                sql_q = f"""
                         UPDATE Questions
                         SET MultiQuestions = {new_id}                          
                         WHERE QuestionId = {new_id} 
                         """
                cursor.execute(sql_q)
                conn.commit()

    def update_answers(self, username, questions_id, answers):
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()
        for i in range(len(answers)):
            sql_q = """
                        IF NOT EXISTS (SELECT * FROM UsersAnswers WHERE QuestionId = ? AND Username = ?)

                        INSERT INTO UsersAnswers(QuestionId, Username, Answer)
                        VALUES(?, ?, ?)
                        
                        ELSE
                        
                        UPDATE UsersAnswers
                        SET QuestionId = ?, Username = ?, Answer = ?
                        WHERE QuestionId = ? AND Username = ?
                                          
                    """
            cursor.execute(sql_q, questions_id[i], username, questions_id[i],
                           username, answers[i], questions_id[i], username, answers[i],
                           questions_id[i], username)
            conn.commit()

    def get_categories_stats(self):
        conn = pyodbc.connect(self.conn_string)
        sql_q = """
                SELECT q.CategoryId, SUM(case when u.Answer= 1 then 1 else 0 end) as Correct, SUM(case when u.Answer = 0  then 1 else 0 end) AS Incorrect
                FROM Questions q JOIN UsersAnswers u
                On q.QuestionId = u.QuestionId
                GROUP BY q.CategoryId
                """
        stats = pd.read_sql(sql_q, conn)
        stats = stats.set_index('CategoryId')
        return stats

    def get_diff_stats(self):
        conn = pyodbc.connect(self.conn_string)
        sql_q = """
                SELECT q.Difficulty, SUM(case when u.Answer= 1 then 1 else 0 end) as Correct, SUM(case when u.Answer = 0  then 1 else 0 end) AS Incorrect
                FROM Questions q JOIN UsersAnswers u
                On q.QuestionId = u.QuestionId
                GROUP BY q.Difficulty
                """
        stats = pd.read_sql(sql_q, conn)
        stats = stats.set_index('Difficulty')
        return stats

    def get_winners(self):
        conn = pyodbc.connect(self.conn_string)
        sql_q = """
                    SELECT TOP 3 u.Username, SUM(case when u.Answer= 1 then 1 else 0 end) as Correct, SUM(case when u.Answer = 0  then 1 else 0 end) AS Incorrect
                    FROM Questions q JOIN UsersAnswers u
                    On q.QuestionId = u.QuestionId
                    GROUP BY u.Username
                    ORDER BY Correct DESC, Incorrect
                 """
        return pd.read_sql(sql_q, conn)

    def get_category(self, category_name):
        """
        Get the catergory I.d which corresponds to the catergory name
        :param category_name:  string category name
        :return:  int category i.d
        """
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()
        sql_q = """
                    SELECT CategoryId
                    FROM Categories
                    WHERE CategoryName = ?
                         """
        return cursor.execute(sql_q, category_name).fetchval()

    def get_categories(self):
        """
        Gets all the possible categories in the database
        :return: list of all the category names
        """
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()
        categories = []
        sql_q = """
                            SELECT CategoryName
                            FROM Categories
                                 """
        rows = cursor.execute(sql_q).fetchall()
        for row in rows:
            categories.append(row.CategoryName)
        return categories