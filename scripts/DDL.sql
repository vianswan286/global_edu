DROP TABLE IF EXISTS courses_required_knowledges CASCADE;
DROP TABLE IF EXISTS courses_final_knowledges CASCADE;
DROP TABLE IF EXISTS tags_collections CASCADE;
DROP TABLE IF EXISTS tags_courses CASCADE;
DROP TABLE IF EXISTS courses_cards CASCADE;
DROP TABLE IF EXISTS knowledges_collections CASCADE;
DROP TABLE IF EXISTS cards_knowledges CASCADE;
DROP TABLE IF EXISTS students_knowledges CASCADE;
DROP TABLE IF EXISTS students_cards CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS collections CASCADE;
DROP TABLE IF EXISTS knowledges CASCADE;
DROP TABLE IF EXISTS cards CASCADE;
DROP TABLE IF EXISTS students CASCADE;


-- 1. STUDENTS (студенты)
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name text NOT NULL,
    email text NOT NULL UNIQUE,
    password_hash text NOT NULL
);
-- Комментарий: Хранит данные о студентах.

-- 2. CARDS (карточки)
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    question text NOT NULL,
    answer text NOT NULL
);
-- Комментарий: Основная сущность для флеш-карточек, тестовых вопросов и т.д.

-- 5. KNOWLEDGES (знания)
CREATE TABLE knowledges (
    id SERIAL PRIMARY KEY,
    name text NOT NULL,
    theory text,
    description text,
    start_date TIMESTAMP,  -- Начало согласно SCD2 (может быть NULL)
    end_date TIMESTAMP     -- Конец согласно SCD2 (может быть NULL)
);
-- Комментарий: Справочник «единиц знаний» (тем, терминов, понятий).

-- 7. COLLECTIONS (коллекции)
CREATE TABLE collections (
    id SERIAL PRIMARY KEY,
    name text NOT NULL,
    description text
);
-- Комментарий: «Подборки» знаний по каким-то темам.

-- 9. COURSES (курсы)
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name text NOT NULL,
    description text
);
-- Комментарий: Содержит информацию об учебных курсах.

-- 11. TAGS (теги)
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name text NOT NULL
);
-- Комментарий: Список возможных тегов (темы, категории и т.д.).


-- 3. STUDENTS_CARDS (прохождение карточек студентами)
CREATE TABLE students_cards (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mark INTEGER,  -- Оценка от 0 до 10; может быть NULL
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (card_id) REFERENCES cards(id)
);
-- Комментарий: Фиксирует факт взаимодействия студента с карточкой.

-- 4. STUDENTS_KNOWLEDGES (общие знания студентов)
CREATE TABLE students_knowledges (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    knowledge_id INTEGER NOT NULL,
    quality INTEGER NOT NULL,  -- Шкала, например, от 0 до 100
    last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (knowledge_id) REFERENCES knowledges(id)
);
-- Комментарий: Обобщённая информация о том, насколько хорошо студент знает определённую тему.

-- 6. CARDS_KNOWLEDGES (знания в карточках)
CREATE TABLE cards_knowledges (
    id SERIAL PRIMARY KEY,
    card_id INTEGER NOT NULL,
    knowledge_id INTEGER NOT NULL,
    quality INTEGER NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id),
    FOREIGN KEY (knowledge_id) REFERENCES knowledges(id)
);
-- Комментарий: Связь многие-к-многим между карточками и знаниями.

-- 8. KNOWLEDGES_COLLECTIONS (знания в коллекциях)
CREATE TABLE knowledges_collections (
    id SERIAL PRIMARY KEY,
    knowledge_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    FOREIGN KEY (knowledge_id) REFERENCES knowledges(id),
    FOREIGN KEY (collection_id) REFERENCES collections(id)
);
-- Комментарий: Связующая таблица многие-к-многим между знаниями и коллекциями.

-- 10. COURSES_CARDS (карточки, связанные с курсом)
CREATE TABLE courses_cards (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (card_id) REFERENCES cards(id)
);
-- Комментарий: Связь многие-к-многим между курсом и карточками, которые используются в курсе.

-- 12. TAGS_COURSES (теги для курсов)
CREATE TABLE tags_courses (
    id SERIAL PRIMARY KEY,
    tag_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY (tag_id) REFERENCES tags(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
-- Комментарий: Модель «многие-к-многим» для привязки тегов к курсам.

-- 13. TAGS_COLLECTIONS (теги для коллекций)
CREATE TABLE tags_collections (
    id SERIAL PRIMARY KEY,
    tag_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    FOREIGN KEY (tag_id) REFERENCES tags(id),
    FOREIGN KEY (collection_id) REFERENCES collections(id)
);
-- Комментарий: Аналогичная модель «многие-к-многим» для привязки тегов к коллекциям.

-- 14. COURSES_FINAL_KNOWLEDGES
CREATE TABLE courses_final_knowledges (
    id BIGSERIAL PRIMARY KEY,
    course_id BIGINT NOT NULL,
    knowledge_id text NOT NULL,
    quality INT NOT NULL,  -- Итоговый уровень знания (0–100)
    FOREIGN KEY (course_id) REFERENCES courses(id)
    -- FOREIGN KEY (knowledge_id) REFERENCES knowledges(id)
    -- не добавлен из-за несоответствия типов (text vs integer)
);
-- Комментарий: Ожидаемый уровень знаний после окончания курса.

-- 15. COURSES_REQUIRED_KNOWLEDGES
CREATE TABLE courses_required_knowledges (
    id BIGSERIAL PRIMARY KEY,
    course_id BIGINT NOT NULL,
    knowledge_id text NOT NULL,
    quality INT NOT NULL,  -- Минимальный (требуемый) уровень знания (0–100)
    FOREIGN KEY (course_id) REFERENCES courses(id)
    -- FOREIGN KEY (knowledge_id) REFERENCES knowledges(id)
    -- не добавлен из-за несоответствия типов (text vs integer)
);
-- Комментарий: Требуемые знания.


------------------------------------------------------
-- Индексы для промежуточных (связующих) таблиц
------------------------------------------------------

-- STUDENTS_CARDS: индексация по внешним ключам
CREATE INDEX idx_students_cards_student_id ON students_cards(student_id);
CREATE INDEX idx_students_cards_card_id ON students_cards(card_id);

-- STUDENTS_KNOWLEDGES: индексация по внешним ключам
CREATE INDEX idx_students_knowledges_student_id ON students_knowledges(student_id);
CREATE INDEX idx_students_knowledges_knowledge_id ON students_knowledges(knowledge_id);

-- CARDS_KNOWLEDGES: индексация по внешним ключам
CREATE INDEX idx_cards_knowledges_card_id ON cards_knowledges(card_id);
CREATE INDEX idx_cards_knowledges_knowledge_id ON cards_knowledges(knowledge_id);

-- KNOWLEDGES_COLLECTIONS: индексация по внешним ключам
CREATE INDEX idx_knowledges_collections_knowledge_id ON knowledges_collections(knowledge_id);
CREATE INDEX idx_knowledges_collections_collection_id ON knowledges_collections(collection_id);

-- COURSES_CARDS: индексация по внешним ключам
CREATE INDEX idx_courses_cards_course_id ON courses_cards(course_id);
CREATE INDEX idx_courses_cards_card_id ON courses_cards(card_id);

-- TAGS_COURSES: индексация по внешним ключам
CREATE INDEX idx_tags_courses_tag_id ON tags_courses(tag_id);
CREATE INDEX idx_tags_courses_course_id ON tags_courses(course_id);

-- TAGS_COLLECTIONS: индексация по внешним ключам
CREATE INDEX idx_tags_collections_tag_id ON tags_collections(tag_id);
CREATE INDEX idx_tags_collections_collection_id ON tags_collections(collection_id);

-- COURSES_FINAL_KNOWLEDGES: индексация по внешним ключам
CREATE INDEX idx_courses_final_knowledges_course_id ON courses_final_knowledges(course_id);
CREATE INDEX idx_courses_final_knowledges_knowledge_id ON courses_final_knowledges(knowledge_id);

-- COURSES_REQUIRED_KNOWLEDGES: индексация по внешним ключам
CREATE INDEX idx_courses_required_knowledges_course_id ON courses_required_knowledges(course_id);
CREATE INDEX idx_courses_required_knowledges_knowledge_id ON courses_required_knowledges(knowledge_id);
