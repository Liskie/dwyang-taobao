import sqlite3
import json

import pandas as pd

from data_models import User, NeutralityEnum, ReplierEnum, SpeechEnum


class DBManager:
    def __init__(self, db_name: str = 'taobao.sqlite'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        sql = '''create table if not exists users (
                    id integer primary key,
                    name text,
                    student_id text unique,
                    gender text,
                    phone text,
                    neutrality_variable text,
                    replier_variable text,
                    speech_variable text,
                    expected_compensation text,
                    conversation text
                 )
        '''
        self.cursor.execute(sql)
        self.conn.commit()

    def insert_user(self, user: User) -> None:
        try:
            sql = '''insert into users (name, student_id, gender, phone, conversation) 
                values (?, ?, ?, ?, ?)
            '''
            data = (user.name, user.student_id, user.gender, user.phone, json.dumps(user.conversation))
            self.cursor.execute(sql, data)
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"User with student_id {user.student_id} already exists.")

    def select_user(self, user: User) -> dict:
        sql = '''select * from users where student_id = ?'''
        data = [user.student_id]
        user_df = pd.read_sql_query(sql, self.conn, params=data)
        if len(user_df) > 1:
            raise Exception('Duplicate user exists!')
        return user_df.iloc[0].to_dict()

    def update_user_conversation(self, user: User, conversation: list[dict[str, str]]) -> None:
        sql = '''update users set conversation = ? where student_id = ?'''
        data = (json.dumps(conversation), user.student_id)
        self.cursor.execute(sql, data)
        self.conn.commit()

    def update_user_variables(self, user: User) -> None:
        user_properties: dict = self.select_user(user)
        user_id: int = user_properties['id']
        flags = list(bin(user_id % 8).lstrip('0b').zfill(3))
        user.neutrality_variable = NeutralityEnum.COURT if flags[0] == '1' else NeutralityEnum.CUSTOMER_SERVICE
        user.replier_variable = ReplierEnum.HUMAN if flags[1] == '1' else ReplierEnum.SYSTEM
        user.speech_variable = SpeechEnum.FREE_TYPING if flags[2] == '1' else SpeechEnum.CHOICES_ONLY
        sql = '''update users 
            set neutrality_variable = ?, replier_variable = ?, speech_variable = ? 
            where id = ?'''
        data = (user.neutrality_variable.value, user.replier_variable.value, user.speech_variable.value, user_id)
        self.cursor.execute(sql, data)
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


if __name__ == '__main__':
    with DBManager() as manager:
        manager.create_table()

