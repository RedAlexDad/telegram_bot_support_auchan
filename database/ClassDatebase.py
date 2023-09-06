import psycopg2

from config import *

class DatabaseLogs():
    def __init__(self):
        self.ID_client = None
        self.ID_correspondence = None
        self.ID_dialog = None


    # Подключение к БД
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
    # Удаление БД
    def drop_table(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                DROP TABLE Client CASCADE;
                DROP TABLE Correspondence CASCADE;
                DROP TABLE Dialog CASCADE;
                """)

            # Подтверждение изменений
            self.connection.commit()
            print("[INFO] Успешно удалены таблицы в базе данных")

        except Exception as ex:
            print("[INFO] Ошибка при работе с PostgreSQL:", ex)
    # Создание таблицы БД и связанные таблицы
    def create_table(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""                                      
                    CREATE TABLE Client (
                        ID_client SERIAL PRIMARY KEY,
                        ID_user INT NOT NULL
                    );
                                                           
                    CREATE TABLE Correspondence (
                    ID_correspondence SERIAL PRIMARY KEY,
                    -- Этот столбец будет автоинкрементным
                    ID_client SERIAL,
                    start_time VARCHAR,
                    end_time VARCHAR
                    );
                                                        
                    CREATE TABLE Dialog (
                    ID_dialog SERIAL PRIMARY KEY,
                    question VARCHAR NOT NULL,
                    answer VARCHAR NOT NULL,
                    intent VARCHAR NOT NULL,
                    common_token INT NOT NULL,
                    time_dialog VARCHAR NOT NULL,
                    voice_status BOOL NOT NULL,
                    photo_status BOOL NOT NULL,
                    ID_correspondence INT NOT NULL
                    );
                    
                                            -- СВЯЗЫВАНИЕ БД ВНЕШНИМИ КЛЮЧАМИ --
                    ALTER TABLE Dialog
                    -- FK_Ord_Cust - имя внешнего ключа для СУБД
                    ADD CONSTRAINT FR_Dialog_Correspondence
                        FOREIGN KEY (ID_correspondence) REFERENCES Correspondence (ID_correspondence);
                    
                    ALTER TABLE Correspondence
                    -- FK_Ord_Cust - имя внешнего ключа для СУБД
                    ADD CONSTRAINT FR_Correspondence_Client
                        FOREIGN KEY (ID_correspondence) REFERENCES Client (ID_client);
                """)

            # Подтверждение изменений
            self.connection.commit()
            print("[INFO] Успешно создана таблица в базе данных")

        except Exception as ex:
            print("[INFO] Ошибка при работе с PostgreSQL:", ex)
    # Вставка значений в таблицы Клиент
    def insert_client(self, ID_user):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO Client (ID_user) VALUES
                        (%s) RETURNING ID_client;""",
                    (ID_user, )
                )

                self.ID_client = cursor.fetchone()[0]

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Ошибка при заполнение данных:", ex)

    def insert_correspondence(self, ID_client, start_time, end_time):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO Correspondence (ID_client, start_time, end_time) VALUES
                        (%s, %s, %s) RETURNING ID_correspondence;""",
                    (ID_client, start_time, end_time)
                )

                self.ID_correspondence = cursor.fetchone()[0]

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Ошибка при заполнение данных:", ex)

    def insert_dialog(self, question, answer, intent, common_token, time_dialog, voice_status, photo_status, ID_correspondence):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO Dialog (question, answer, intent, common_token, time_dialog, voice_status, photo_status, ID_correspondence) VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s);""",
                    (question, answer, intent, common_token, time_dialog, voice_status, photo_status, ID_correspondence)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Ошибка при заполнение данных:", ex)

    # Обновление данных таблицы переписок
    def update_correspondence_end_time(self, ID_client, end_time):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE Correspondence SET end_time = (%s) WHERE ID_client = (%s);""",
                    (end_time, ID_client)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] Данные успешно обновлено")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Ошибка при обновление данных:", ex)

    def select_all(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM Client;""")
            print('='*100)
            print('CLIENT')
            print('-'*100)
            self.print_db(cursor.fetchall())

            cursor.execute("""SELECT * FROM Correspondence;""")
            print('='*100)
            print('Correspondence')
            print('-'*100)
            self.print_db(cursor.fetchall())

            cursor.execute("""SELECT * FROM Dialog;""")
            print('='*100)
            print('Dialog')
            print('-'*100)
            self.print_db(cursor.fetchall())
            print('='*100)
    def print_db(self, rows):
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