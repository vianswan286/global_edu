import os
import sys
import pytest
import re
import psycopg2
from psycopg2.extras import RealDictCursor

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import DB_CONFIG

def get_db_connection():
    # Соединение с БД
    conn = psycopg2.connect(
        dbname=DB_CONFIG['name'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
    return conn

def read_sql_queries(file_path):
    # Чтение SQL-запросов из файла
    with open(file_path, 'r') as f:
        content = f.read()
    parsed_queries = []
    query_blocks = re.split(r'\n\s*\n', content)
    for block in query_blocks:
        if not block.strip():
            continue
        comment_match = re.search(r'--(.+?)--', block)
        description = comment_match.group(1).strip() if comment_match else "SQL Query"
        query_lines = [line for line in block.split('\n') if not line.strip().startswith('--') or line.strip() == '']
        query = '\n'.join(query_lines).strip()
        if query.endswith(';'):
            query = query[:-1].strip()
        if query:
            parsed_queries.append({'description': description, 'query': query})
    return parsed_queries

class TestSQLRequests:
    @classmethod
    def setup_class(cls):
        # Открываем соединение один раз
        cls.conn = get_db_connection()
        cls.queries = read_sql_queries(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'requests.sql'))

    @classmethod
    def teardown_class(cls):
        # Закрываем соединение
        cls.conn.close()

    def execute_query(self, query):
        # Выполнить SQL-запрос
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            try:
                results = cursor.fetchall()
                return results
            except psycopg2.ProgrammingError:
                self.conn.commit()
                return []

    def test_01_course_cards(self):
        # Карточки первого курса
        query_info = next((q for q in self.queries if 'cards' in q['query'].lower() and 'course_id = 1' in q['query']), None)
        assert query_info is not None
        results = self.execute_query(query_info['query'])
        assert isinstance(results, list)
        assert len(results) > 0
        for row in results:
            assert "id" in row
            assert "question" in row
            assert "answer" in row

    def test_02_student_ranking_by_average_marks(self):
        # Рейтинг студентов по средним оценкам
        query_info = next((q for q in self.queries if 'average_mark' in q['query'] and 'RANK()' in q['query']), None)
        assert query_info is not None
        results = self.execute_query(query_info['query'])
        assert isinstance(results, list)
        if results:
            assert "student_rank" in results[0]
            assert "average_mark" in results[0]
            ranks = [row['student_rank'] for row in results]
            for i in range(1, len(ranks)):
                assert ranks[i] >= ranks[i-1]

    def test_03_student_ranking_by_knowledge_count(self):
        # Рейтинг студентов по знаниям из первой коллекции
        query_info = next((q for q in self.queries if 'knowledges_count' in q['query'] and 'collection_id = 1' in q['query']), None)
        assert query_info is not None
        results = self.execute_query(query_info['query'])
        assert isinstance(results, list)
        if results:
            assert "student_rank" in results[0]
            assert "knowledges_count" in results[0]
            ranks = [row['student_rank'] for row in results]
            for i in range(1, len(ranks)):
                assert ranks[i] >= ranks[i-1]


    def test_05_filter_students_by_marks_and_cards(self):
        # Студенты с >=1 карточкой и средней оценкой >=7
        query_info = next((q for q in self.queries if 'HAVING' in q['query'] and 'AVG(sc.mark)' in q['query']), None)
        assert query_info is not None
        results = self.execute_query(query_info['query'])
        assert isinstance(results, list)
        if results:
            assert "average_mark" in results[0]
            assert "cards_attempted" in results[0]
            for row in results:
                assert row['average_mark'] >= 7
                assert row['cards_attempted'] >= 1

    def test_06_course_final_knowledge(self):
        # Финальные знания по курсам
        query_info = next((q for q in self.queries if 'WITH card_quality' in q['query'] and 'total_quality' in q['query']), None)
        assert query_info is not None
        results = self.execute_query(query_info['query'])
        assert isinstance(results, list)
        if results:
            assert "course_id" in results[0]
            assert "knowledge_id" in results[0]
            assert "total_quality" in results[0]

    def test_07_login_check(self):
        # Проверка логина
        query_info = next((q for q in self.queries if 'EXISTS' in q['query'] and 'password_hash' in q['query']), None)
        assert query_info is not None
        results = self.execute_query(query_info['query'])
        assert isinstance(results, list)
        assert len(results) == 1
        assert "hash_exists" in results[0]

    def test_08_courses_by_tag(self):
        # Курсы по тегу
        query_info = next((q for q in self.queries if 'tags_courses' in q['query'] and "t.name = 'ООП'" in q['query']), None)
        assert query_info is not None
        results = self.execute_query(query_info['query'])
        assert isinstance(results, list)
        if results:
            assert "id" in results[0]
            assert "name" in results[0]
            assert "description" in results[0]

    def test_09_knowledge_ranking(self):
        # Рейтинг знаний
        query_info = next((q for q in self.queries if 'knowledge_rank' in q['query'] and 'AVG(sk.quality)' in q['query']), None)
        assert query_info is not None
        results = self.execute_query(query_info['query'])
        assert isinstance(results, list)
        if results:
            assert "knowledge_rank" in results[0]
            assert "avg_quality" in results[0]
            ranks = [row['knowledge_rank'] for row in results]
            for i in range(1, len(ranks)):
                assert ranks[i] >= ranks[i-1]

    def test_10_card_question_answer(self):
        # Вопрос и ответ по карте
        query_info = next((q for q in self.queries if 'question' in q['query'] and 'answer' in q['query'] and 'WHERE id = 1' in q['query']), None)
        assert query_info is not None
        results = self.execute_query(query_info['query'])
        assert isinstance(results, list)
        assert len(results) == 1
        assert "id" in results[0]
        assert "question" in results[0]
        assert "answer" in results[0]

if __name__ == "__main__":
    pytest.main(["-v", __file__])
