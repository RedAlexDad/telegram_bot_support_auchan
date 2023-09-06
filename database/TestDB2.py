import psycopg2

try:
    # Параметры подключения к базе данных
    host = "localhost"
    user = "postgres"
    password = "postgres"
    db_name = "postgres"

    # Подключение к базе данных
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    # Создание таблицы
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Employees (
                Id SERIAL PRIMARY KEY,
                FirstName VARCHAR(50) NOT NULL,
                LastName VARCHAR(50) NOT NULL,
                Department VARCHAR(50)
            );
        """)

    # Подтверждение изменений
    connection.commit()
    print("Таблица успешно создана")

except Exception as ex:
    print("Ошибка при работе с PostgreSQL:", ex)

finally:
    # Закрытие соединения
    if connection:
        connection.close()
