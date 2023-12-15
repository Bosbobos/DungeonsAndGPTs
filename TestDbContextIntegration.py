import unittest
import json
import psycopg2
from DbContext import DbContext  # Замените "your_module" на имя вашего модуля

class TestDbContext(unittest.TestCase):
    def setUp(self):
        # Чтение настроек из файла appsettings.json
        with open('appsettings.json', 'r') as file:
            settings = json.load(file)

        # Используйте настройки тестовой базы данных
        self.test_db_config = settings['DbConnection']
        self.db_context = DbContext(**self.test_db_config)

        # Создание тестовой таблицы
        self.create_test_table()

    def tearDown(self):
        # Удаление тестовой таблицы
        self.drop_test_table()

    def create_test_table(self):
        conn = self.db_context.connect()
        cursor = conn.cursor()

        # Замените 'your_table_name' на имя вашей таблицы и определение колонок
        create_table_query = """
        CREATE TABLE IF NOT EXISTS your_table_name (
            id SERIAL PRIMARY KEY,
            column1 VARCHAR(255),
            column2 VARCHAR(255)
        );
        """
        cursor.execute(create_table_query)
        conn.commit()

        cursor.close()
        conn.close()

    def drop_test_table(self):
        conn = self.db_context.connect()
        cursor = conn.cursor()

        # Замените 'your_table_name' на имя вашей таблицы
        drop_table_query = "DROP TABLE IF EXISTS your_table_name;"
        cursor.execute(drop_table_query)
        conn.commit()

        cursor.close()
        conn.close()

    def test_create_read_update_delete_record(self):
        # Тест для создания, чтения, обновления и удаления записи

        # Создаем запись
        record_data = {'column1': 'value1', 'column2': 'value2'}
        self.db_context.create_record('your_table_name', record_data)

        # Читаем созданную запись
        read_record = self.db_context.read_record('your_table_name', 'column1', 'value1')
        self.assertIsNotNone(read_record)

        # Обновляем созданную запись
        update_data = {'column2': 'updated_value'}
        self.db_context.update_record('your_table_name', 'column1', 'value1', update_data)

        # Проверяем, что запись была успешно обновлена
        updated_record = self.db_context.read_record('your_table_name', 'column1', 'value1')
        self.assertEqual(updated_record['column2'], 'updated_value')

        # Удаляем созданную запись
        self.db_context.delete_record('your_table_name', 'column1', 'value1')

        # Проверяем, что запись успешно удалена
        deleted_record = self.db_context.read_record('your_table_name', 'column1', 'value1')
        self.assertIsNone(deleted_record)

if __name__ == '__main__':
    unittest.main()
