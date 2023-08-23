import psycopg2

from config import *

class DatabaseLogs():
    def connect(self):
        try:
            # Подключение к базе данных
            self.connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )

            print("[INFO] Успешное подключение к базе данных")

        except Exception as ex:
            print("[INFO] Ошибка при работе с PostgreSQL:", ex)

    def create_table(self):
        try:
            # Создание таблицы
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Logs (
                        ID SERIAL PRIMARY KEY,
                        Name VARCHAR NOT NULL,
                        prompt VARCHAR NOT NULL,
                        answer VARCHAR NOT NULL,
                        common_token INT NOT NULL,
                        datetime VARCHAR NOT NULL,
                        voice_status BOOL NOT NULL,
                        photo_status BOOL NOT NULL
                    );
                """)

            # Подтверждение изменений
            self.connection.commit()
            print("[INFO] Успешно создана таблица в базе данных")

        except Exception as ex:
            print("[INFO] Ошибка при работе с PostgreSQL:", ex)
    def insert(self, ID, Name, prompt, answer, common_token, datetime, voice_status, photo_status):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO Log (ID, Name, prompt, answer, common_token, datetime, voice_status, photo_status) VALUES
                	(%s, %s, %s, %s, %s, %s, %s, %s);""",
                (ID, Name, prompt, answer, common_token, datetime, voice_status, photo_status)
            )

            # Подтверждение изменений
            self.connection.commit()
            print("[INFO] Данные успешно вставлены")

    def select_all(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Log;")
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    print(row)
            else:
                print("Таблица пуста")

    def close(self):
        # Закрытие соединения
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")