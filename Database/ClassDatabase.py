import psycopg2

from config import database, host, port, user, sslmode, password, dbname, target_session_attrs

class DatabaseLogs():
    def __init__(self):
        self.ID_client = None

    # Подключение к БД
    def connect(self):
        try:
            # Подключение к базе данных

            # С локального места (с ноутбука, компьютера)
            try:
                self.connection = psycopg2.connect(
                    dbname=dbname,
                    host=host,
                    port=port,
                    sslmode=sslmode,
                    user=user,
                    password=password,
                    target_session_attrs=target_session_attrs
                )
            # С облачного сервиса (Yandex Cloud Functions)
            # Отличие от вышеописанных здесь заключается в следующем - отсутствует защищенный протокол sslmode
            except:
                self.connection = psycopg2.connect(
                    dbname = dbname,
                    host = host,
                    port = port,
                    user = user,
                    password = password,
                    target_session_attrs = target_session_attrs
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
                DROP TABLE Dialog CASCADE;
                DROP TABLE Emotion CASCADE;
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
                    CREATE TABLE client (
                    ID SERIAL PRIMARY KEY,
                    ID_user INT NOT NULL,
                    start_time VARCHAR NOT NULL,
                    end_time VARCHAR NOT NULL,
                    smile_status VARCHAR NOT NULL
                    );

                    CREATE TABLE dialog (
                    ID_dialog SERIAL PRIMARY KEY,
                    question VARCHAR NOT NULL,
                    answer VARCHAR NOT NULL,
                    intent VARCHAR NOT NULL,
                    common_token INT NOT NULL,
                    time_dialog VARCHAR NOT NULL,
                    voice_file VARCHAR NOT NULL,
                    photo_file VARCHAR NOT NULL,
                    ID_client INT NOT NULL
                    );
                    
                    CREATE TABLE emotion (
                        ID_emotion SERIAL PRIMARY KEY,
                        label VARCHAR NOT NULL,
                        score FLOAT NOT NULL,
                        ID_dialog INT REFERENCES Dialog(ID_dialog)
                    );


                                            -- СВЯЗЫВАНИЕ БД ВНЕШНИМИ КЛЮЧАМИ --
                    ALTER TABLE Dialog
                    ADD CONSTRAINT FR_Dialog_Client
                        FOREIGN KEY (ID_client) REFERENCES Client (ID);
                        
                    ALTER TABLE Emotion
                    ADD CONSTRAINT FR_Emotion_Dialog
                        FOREIGN KEY (ID_dialog) REFERENCES Dialog (ID_dialog);
                    """)

            # Подтверждение изменений
            self.connection.commit()
            print("[INFO] Успешно создана таблица в базе данных")

        except Exception as ex:
            print("[INFO] Ошибка при работе с PostgreSQL:", ex)

    # Вставка значений в таблицы Клиент
    def insert_client(self, ID_user, start_time, end_time, smile_status):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO Client (ID_user, start_time, end_time, smile_status) VALUES
                        (%s, %s, %s, %s) RETURNING ID;""",
                    (ID_user, start_time, end_time, smile_status)
                )

                self.ID_client = cursor.fetchone()[0]

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] Client Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Client Ошибка при заполнение данных:", ex)

    def insert_dialog(self, question, answer, intent, common_token, time_dialog, voice_file, photo_file, ID_client):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO Dialog (question, answer, intent, common_token, time_dialog, voice_file, photo_file, ID_client) VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING ID_dialog;""",
                    (question, answer, intent, common_token, time_dialog, voice_file, photo_file, ID_client)
                )

                self.ID_dialog = cursor.fetchone()[0]

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] Dialog Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Dialog Ошибка при заполнение данных:", ex)

    def insert_emotion(self, label, score, ID_dialog):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO Emotion (label, score, ID_dialog) VALUES
                        (%s, %s, %s);""",
                    (label, score, ID_dialog)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] Emotion Данные успешно вставлены")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Emotion Ошибка при заполнение данных:", ex)

    # Обновление данных таблицы переписок
    def update_correspondence_end_time(self, end_time, smile_status, ID_client):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE Client SET end_time = %s, smile_status = %s WHERE ID = %s;""",
                    (end_time, smile_status, ID_client)
                )

                # Подтверждение изменений
                self.connection.commit()
                print("[INFO] Данные успешно обновлено")
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Ошибка при обновление данных:", ex)

    def select_all(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""SELECT * FROM Client;""")
                clients = self.fetch_records(cursor)

                cursor.execute("""SELECT * FROM Dialog;""")
                dialogs = self.fetch_records(cursor)

                return clients, dialogs
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Ошибка при обновление данных:", ex)

    def fetch_records(self, cursor):
        rows = cursor.fetchall()
        if rows:
            return rows
        else:
            return None

    def request(self, request_text:str):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(request_text)
                column_names = [desc[0] for desc in cursor.description]

                response = self.fetch_records(cursor)

                return response, column_names
        except Exception as ex:
            # Откат транзакции в случае ошибки
            self.connection.rollback()
            print("[INFO] Ошибка при обновление данных:", ex)

    def close(self):
        # Закрытие соединения
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")