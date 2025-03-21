SELECT id, name, email
FROM students;

INSERT INTO students (name, email, password_hash)
VALUES ('John Doe', 'john.doe@example.com', 'hashed_password_here');

SELECT c.id, c.question, c.answer
FROM cards c
JOIN courses_cards cc ON c.id = cc.card_id
WHERE cc.course_id = 1;

SELECT c.id, c.question, c.answer
FROM cards c
JOIN courses_cards cc ON c.id = cc.card_id
WHERE cc.course_id = 1;

SELECT sc.id, sc.time, sc.mark, c.question, c.answer
FROM students_cards sc
JOIN cards c ON sc.card_id = c.id
WHERE sc.student_id = 1;

SELECT sk.knowledge_id, k.name, sk.quality, sk.last_update
FROM students_knowledges sk
JOIN knowledges k ON sk.knowledge_id = k.id
WHERE sk.student_id = 1;

SELECT k.id, k.name, k.description
FROM knowledges k
JOIN cards_knowledges ck ON k.id = ck.knowledge_id
WHERE ck.card_id = 2;

SELECT col.id, col.name, col.description
FROM collections col
JOIN knowledges_collections kc ON col.id = kc.collection_id
WHERE kc.knowledge_id = 1;

SELECT co.id, co.name, co.description
FROM courses co
JOIN tags_courses tc ON co.id = tc.course_id
JOIN tags t ON tc.tag_id = t.id
WHERE t.name = 'Mathematics';

UPDATE students_cards
SET mark = 8
WHERE student_id = 1 AND card_id = 2;
