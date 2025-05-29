--все карточки из первого курса--
SELECT c.id, c.question, c.answer
FROM cards c
JOIN courses_cards cc ON c.id = cc.card_id
WHERE cc.course_id = 1;


--рейтинг студентов по средним оценкам--
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
ORDER BY average_mark DESC;


--рейтинг студентов по количеству знаний из первой коллекции--
SELECT
    s.id,
    s.name,
    COUNT(kc.knowledge_id) AS knowledges_count,
    RANK() OVER (ORDER BY COUNT(kc.knowledge_id) DESC) AS student_rank
FROM students s
LEFT JOIN students_knowledges sk ON s.id = sk.student_id
LEFT JOIN knowledges_collections kc ON sk.knowledge_id = kc.knowledge_id AND kc.collection_id = 1
GROUP BY s.id, s.name
ORDER BY knowledges_count DESC;


--поставить оценку 8 студенту 1 за карту 2--
UPDATE students_cards
SET mark = 8
WHERE student_id = 1 AND card_id = 2;


--отбор студентв с хотябы одной карточкой и средней оценкой не ниже 7--
SELECT
    s.id,
    s.name,
    AVG(sc.mark) AS average_mark,
    COUNT(sc.id) AS cards_attempted
FROM students s
JOIN students_cards sc ON s.id = sc.student_id
GROUP BY s.id, s.name
HAVING COUNT(sc.id) >= 1 AND AVG(sc.mark) >= 7
ORDER BY average_mark DESC;


--ищет финальные знания для курсов. Это кэшируется в таблице: courses_final_knowledges, но сами
--данные получаются именно таким образом
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
ORDER BY c.id, cq.total_quality DESC;




--проверка логина--
SELECT EXISTS (
    SELECT 1
    FROM students 
    WHERE email = 'alexey.sidorov@example.com'
      AND password_hash = 'hash_a1'
) AS hash_exists;


--все кеурсы по тегу ООП--
SELECT DISTINCT
    c.id,
    c.name,
    c.description
FROM courses c
JOIN tags_courses tc ON c.id = tc.course_id
JOIN tags t ON t.id = tc.tag_id
WHERE t.name = 'ООП'
ORDER BY c.name;


--рейтинг знаний по их освоению--
SELECT 
    k.id AS knowledge_id,
    k.name AS knowledge_name,
    COALESCE(AVG(sk.quality), 0) AS avg_quality,
    RANK() OVER (ORDER BY COALESCE(AVG(sk.quality), 0) DESC) AS knowledge_rank
FROM knowledges k
LEFT JOIN students_knowledges sk ON k.id = sk.knowledge_id
GROUP BY k.id, k.name
ORDER BY avg_quality DESC;


--вывод вопроса и ответа по карте--
SELECT 
    id,
    question,
    answer
FROM cards
WHERE id = 1;
