import os
import sys
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import DB_CONFIG

def get_db_connection():
    # Connect to the database
    conn = psycopg2.connect(
        dbname=DB_CONFIG['name'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
    return conn

class TestSQLRequests:
    @classmethod
    def setup_class(cls):
        # Open connection once
        cls.conn = get_db_connection()
        
        # Hardcoded SQL queries
        cls.queries = {
            "course_cards": {
                "query": """
                SELECT c.id, c.question, c.answer
                FROM cards c
                JOIN courses_cards cc ON c.id = cc.card_id
                WHERE cc.course_id = 1
                """,
                "expected_results": [
                    {"id": 1, "question": "Что такое сложение?", "answer": "Сложение - это арифметическая операция, объединяющая два числа в одно."},
                    {"id": 2, "question": "Как найти НОД двух чисел?", "answer": "Для нахождения наибольшего общего делителя можно использовать алгоритм Евклида."},
                    {"id": 3, "question": "Что такое дробь?", "answer": "Дробь - это число, представляющее часть целого. Записывается как отношение двух чисел."},
                    {"id": 4, "question": "Как сложить дроби с разными знаменателями?", "answer": "Нужно привести дроби к общему знаменателю, а затем сложить числители."},
                    {"id": 5, "question": "Как умножить две дроби?", "answer": "При умножении дробей нужно умножить числитель на числитель, а знаменатель на знаменатель."}
                ]
            },
            "student_ranking_by_average_marks": {
                "query": """
                SELECT
                    id,
                    name,
                    average_mark,
                    RANK() OVER (ORDER BY average_mark DESC) AS student_rank
                FROM (
                    SELECT
                        s.id,
                        s.name,
                        AVG(sc.mark) AS average_mark
                    FROM students s
                    LEFT JOIN students_cards sc ON s.id = sc.student_id
                    GROUP BY s.id, s.name
                ) AS student_avg
                ORDER BY average_mark DESC
                """,
                "expected_results": [
                    {"id": 1, "name": "Demo User", "average_mark": 8.0, "student_rank": 1}
                ]
            },
            "student_ranking_by_knowledge_count": {
                "query": """
                SELECT
                    s.id,
                    s.name,
                    COUNT(kc.knowledge_id) AS knowledges_count,
                    RANK() OVER (ORDER BY COUNT(kc.knowledge_id) DESC) AS student_rank
                FROM students s
                LEFT JOIN students_knowledges sk ON s.id = sk.student_id
                LEFT JOIN knowledges_collections kc ON sk.knowledge_id = kc.knowledge_id AND kc.collection_id = 1
                GROUP BY s.id, s.name
                ORDER BY knowledges_count DESC
                """,
                "expected_results": [
                    {"id": 1, "name": "Demo User", "knowledges_count": 0, "student_rank": 1},
                    {"id": 2, "name": "sasha", "knowledges_count": 0, "student_rank": 1},
                    {"id": 3, "name": "Иван Петров", "knowledges_count": 0, "student_rank": 1}
                ]
            },
            "filter_students_by_marks_and_cards": {
                "query": """
                SELECT
                    s.id,
                    s.name,
                    AVG(sc.mark) AS average_mark,
                    COUNT(sc.id) AS cards_attempted
                FROM students s
                JOIN students_cards sc ON s.id = sc.student_id
                GROUP BY s.id, s.name
                HAVING COUNT(sc.id) >= 1 AND AVG(sc.mark) >= 7
                ORDER BY average_mark DESC
                """,
                "expected_results": [
                    {"id": 1, "name": "Алексей Сидоров", "average_mark": 8.0, "cards_attempted": 1}
                ]
            },
            "course_final_knowledge": {
                "query": """
                WITH card_quality AS (
                    SELECT
                        cc.course_id,
                        ck.knowledge_id,
                        SUM(ck.quality) AS total_quality
                    FROM courses_cards cc
                    JOIN cards_knowledges ck ON cc.card_id = ck.card_id
                    GROUP BY cc.course_id, ck.knowledge_id
                )
                SELECT
                    c.id AS course_id,
                    c.name AS course_name,
                    k.id AS knowledge_id,
                    k.name AS knowledge_name,
                    cq.total_quality
                FROM card_quality cq
                JOIN courses c ON cq.course_id = c.id
                JOIN knowledges k ON cq.knowledge_id = k.id
                ORDER BY c.id, cq.total_quality DESC
                """,
                "expected_results": []
            },
            "login_check": {
                "query": """
                SELECT EXISTS (
                    SELECT 1
                    FROM students 
                    WHERE email = 'alexey.sidorov@example.com'
                      AND password_hash = 'hash_a1'
                ) AS hash_exists
                """,
                "expected_results": [
                    {"hash_exists": False}
                ]
            },
            "courses_by_tag": {
                "query": """
                SELECT DISTINCT
                    c.id,
                    c.name,
                    c.description
                FROM courses c
                JOIN tags_courses tc ON c.id = tc.course_id
                JOIN tags t ON t.id = tc.tag_id
                WHERE t.name = 'ООП'
                ORDER BY c.name
                """,
                "expected_results": []
            },
            "knowledge_ranking": {
                "query": """
                SELECT 
                    k.id AS knowledge_id,
                    k.name AS knowledge_name,
                    COALESCE(AVG(sk.quality), 0) AS avg_quality,
                    RANK() OVER (ORDER BY COALESCE(AVG(sk.quality), 0) DESC) AS knowledge_rank
                FROM knowledges k
                LEFT JOIN students_knowledges sk ON k.id = sk.knowledge_id
                GROUP BY k.id, k.name
                ORDER BY avg_quality DESC
                """,
                "expected_results": [
                    {"knowledge_id": 1, "knowledge_name": "Понятие числа", "avg_quality": 0.0, "knowledge_rank": 1},
                    {"knowledge_id": 2, "knowledge_name": "Натуральные числа", "avg_quality": 0.0, "knowledge_rank": 1},
                    {"knowledge_id": 3, "knowledge_name": "Целые числа", "avg_quality": 0.0, "knowledge_rank": 1}
                ]
            },
            "card_question_answer": {
                "query": """
                SELECT 
                    id,
                    question,
                    answer
                FROM cards
                WHERE id = 1
                """,
                "expected_results": [
                    {"id": 1, "question": "Что такое сложение?", "answer": "Сложение - это арифметическая операция, объединяющая два числа в одно."}
                ]
            }
        }

    @classmethod
    def teardown_class(cls):
        # Close connection
        cls.conn.close()

    def execute_query(self, query):
        # Execute SQL query
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            try:
                results = cursor.fetchall()
                return results
            except psycopg2.ProgrammingError:
                self.conn.commit()
                return []

    def test_01_course_cards(self):
        # Cards from the first course
        query_info = self.queries["course_cards"]
        results = self.execute_query(query_info["query"])
        
        # Check structure
        assert isinstance(results, list)
        assert len(results) == len(query_info["expected_results"])
        
        # Check specific results
        for expected in query_info["expected_results"]:
            matching_result = next((r for r in results if r["id"] == expected["id"]), None)
            assert matching_result is not None, f"Expected result with id {expected['id']} not found"
            assert matching_result["question"] == expected["question"]
            assert matching_result["answer"] == expected["answer"]


    def test_05_filter_students_by_marks_and_cards(self):
        # Students with >=1 card and average mark >=7
        query_info = self.queries["filter_students_by_marks_and_cards"]
        results = self.execute_query(query_info["query"])
        
        # Check structure
        assert isinstance(results, list)
        
        # Check filtering criteria
        for row in results:
            assert float(row["average_mark"]) >= 7
            assert row["cards_attempted"] >= 1
            
        # If we have expected results and actual results
        if query_info["expected_results"] and results:
            expected = query_info["expected_results"][0]
            matching_result = next((r for r in results if r["id"] == expected["id"]), None)
            if matching_result:
                assert matching_result["name"] == expected["name"]
                assert abs(float(matching_result["average_mark"]) - expected["average_mark"]) < 0.1
                assert matching_result["cards_attempted"] == expected["cards_attempted"]

    def test_06_course_final_knowledge(self):
        # Final knowledge for courses
        query_info = self.queries["course_final_knowledge"]
        results = self.execute_query(query_info["query"])
        
        # Check structure
        assert isinstance(results, list)
        
        # If we have results, they should have the expected structure
        if results:
            assert "course_id" in results[0]
            assert "course_name" in results[0]
            assert "knowledge_id" in results[0]
            assert "knowledge_name" in results[0]
            assert "total_quality" in results[0]

    def test_07_login_check(self):
        # Login check
        query_info = self.queries["login_check"]
        results = self.execute_query(query_info["query"])
        
        # Check structure
        assert isinstance(results, list)
        assert len(results) == 1
        
        # Check specific results
        assert results[0]["hash_exists"] == query_info["expected_results"][0]["hash_exists"]

    def test_08_courses_by_tag(self):
        # Courses by tag
        query_info = self.queries["courses_by_tag"]
        results = self.execute_query(query_info["query"])
        
        # Check structure
        assert isinstance(results, list)
        
        # If we have expected results and actual results match
        if query_info["expected_results"] and results:
            assert len(results) == len(query_info["expected_results"])
            for expected in query_info["expected_results"]:
                matching_result = next((r for r in results if r["id"] == expected["id"]), None)
                assert matching_result is not None
                assert matching_result["name"] == expected["name"]
                assert matching_result["description"] == expected["description"]

    def test_09_knowledge_ranking(self):
        # Knowledge ranking
        query_info = self.queries["knowledge_ranking"]
        results = self.execute_query(query_info["query"])
        
        # Check structure
        assert isinstance(results, list)
        assert len(results) >= len(query_info["expected_results"])
        
        # Check specific results
        for expected in query_info["expected_results"]:
            matching_result = next((r for r in results if r["knowledge_id"] == expected["knowledge_id"]), None)
            assert matching_result is not None
            assert matching_result["knowledge_name"] == expected["knowledge_name"]
            assert abs(float(matching_result["avg_quality"]) - expected["avg_quality"]) < 0.1
            
        # Check ranking order
        ranks = [row["knowledge_rank"] for row in results]
        for i in range(1, len(ranks)):
            assert ranks[i] >= ranks[i-1]

    def test_10_card_question_answer(self):
        # Question and answer for a card
        query_info = self.queries["card_question_answer"]
        results = self.execute_query(query_info["query"])
        
        # Check structure
        assert isinstance(results, list)
        assert len(results) == 1
        
        # Check specific results
        assert results[0]["id"] == query_info["expected_results"][0]["id"]
        assert results[0]["question"] == query_info["expected_results"][0]["question"]
        assert results[0]["answer"] == query_info["expected_results"][0]["answer"]

if __name__ == "__main__":
    pytest.main(["-v", __file__])
