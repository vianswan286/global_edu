-- =====================================
-- Представления (Views)
-- =====================================

-- 1. Прогресс знаний студентов
CREATE OR REPLACE VIEW student_knowledge_progress AS
SELECT
    s.id AS student_id,
    s.name AS student_name,
    s.email AS student_email,
    k.id AS knowledge_id,
    k.name AS knowledge_name,
    sk.quality,
    sk.last_update
FROM students s
JOIN students_knowledges sk ON sk.student_id = s.id
JOIN knowledges k ON k.id = sk.knowledge_id;
-- Example usage: SELECT get_course_estimated_time(1);
-- 2. Пробелы знаний для курсов
CREATE OR REPLACE VIEW course_knowledge_gap AS
SELECT
    c.id AS course_id,
    c.name AS course_name,
    s.id AS student_id,
    s.name AS student_name,
    k.id AS knowledge_id,
    k.name AS knowledge_name,
    crk.quality AS required_quality,
    COALESCE(sk.quality, 0) AS student_quality
FROM courses c
JOIN courses_required_knowledges crk ON crk.course_id = c.id
JOIN knowledges k ON k.id::text = crk.knowledge_id
CROSS JOIN students s
LEFT JOIN students_knowledges sk ON sk.student_id = s.id AND sk.knowledge_id = k.id
WHERE COALESCE(sk.quality, 0) < crk.quality;

-- =====================================
-- Процедура (Procedure)
-- =====================================

-- Отметить карточку и обновить знание
CREATE OR REPLACE PROCEDURE mark_card_and_update_knowledge(
    IN p_student_id INT,
    IN p_card_id INT,
    IN p_mark INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    k_id INT;
    quality_gain INT;
BEGIN
    -- Отметить карточку
    INSERT INTO students_cards (student_id, card_id, mark, time)
    VALUES (p_student_id, p_card_id, p_mark, NOW())
    ON CONFLICT (student_id, card_id) DO UPDATE SET mark = EXCLUDED.mark, time = NOW();

    -- Для всех знаний, связанных с карточкой, обновить качество
    FOR k_id, quality_gain IN
        SELECT ck.knowledge_id, ck.quality FROM cards_knowledges ck WHERE ck.card_id = p_card_id
    LOOP
        UPDATE students_knowledges sk
        SET quality = LEAST(100, sk.quality + (p_mark * quality_gain)), last_update = NOW()
        WHERE sk.student_id = p_student_id AND sk.knowledge_id = k_id;
    END LOOP;
END;
$$;

-- =====================================
-- Функции (Functions)
-- =====================================

-- Получить качество знания студента
CREATE OR REPLACE FUNCTION get_student_knowledge(p_student_id INT, p_knowledge_id INT)
RETURNS INT AS $$
    SELECT quality FROM students_knowledges WHERE student_id = p_student_id AND knowledge_id = p_knowledge_id;
$$ LANGUAGE SQL;

-- Получить процент завершения курса студентом
CREATE OR REPLACE FUNCTION get_course_completion(p_student_id INT, p_course_id INT)
RETURNS NUMERIC AS $$
DECLARE
    total_required INT;
    completed INT;
BEGIN
    SELECT COUNT(*) INTO total_required FROM courses_required_knowledges WHERE course_id = p_course_id;
    SELECT COUNT(*) INTO completed
    FROM courses_required_knowledges crk
    JOIN students_knowledges sk ON sk.knowledge_id::text = crk.knowledge_id AND sk.student_id = p_student_id
    WHERE crk.course_id = p_course_id AND sk.quality >= crk.quality;
    IF total_required = 0 THEN
        RETURN 1;
    END IF;
    RETURN completed::NUMERIC / total_required;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- Триггеры (Triggers)
-- =====================================

-- 1. При решении карточки обновляет знания
CREATE OR REPLACE FUNCTION trg_update_knowledge_on_card_mark() RETURNS TRIGGER AS $$
DECLARE
    k_id INT;
    quality_gain INT;
BEGIN
    FOR k_id, quality_gain IN SELECT ck.knowledge_id, ck.quality FROM cards_knowledges ck WHERE ck.card_id = NEW.card_id
    LOOP
        UPDATE students_knowledges sk
        SET quality = LEAST(100, sk.quality + (NEW.mark * quality_gain)), last_update = NOW()
        WHERE sk.student_id = NEW.student_id AND sk.knowledge_id = k_id;
    END LOOP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_knowledge_on_card_mark ON students_cards;
CREATE TRIGGER trg_update_knowledge_on_card_mark
AFTER INSERT OR UPDATE ON students_cards
FOR EACH ROW EXECUTE FUNCTION trg_update_knowledge_on_card_mark();

-- Добавим уникальный индекс на таблицу students_cards для колонок student_id и card_id
CREATE UNIQUE INDEX IF NOT EXISTS unique_student_card ON students_cards (student_id, card_id);

-- 2. При добавлении карточки в курс – всем студентам курса добавить “назначение” карточки (пример: добавить запись в students_cards с NULL mark)
CREATE OR REPLACE FUNCTION trg_assign_card_to_all_students() RETURNS TRIGGER AS $$
BEGIN
    -- Добавляем записи с проверкой на дубликаты
    BEGIN
        -- Make sure to include the time field when inserting
        INSERT INTO students_cards (student_id, card_id, time)
        SELECT id, NEW.card_id, NOW() FROM students;
    EXCEPTION WHEN unique_violation THEN
        -- Игнорируем дубликаты
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_assign_card_to_all_students ON courses_cards;
CREATE TRIGGER trg_assign_card_to_all_students
AFTER INSERT ON courses_cards
FOR EACH ROW EXECUTE FUNCTION trg_assign_card_to_all_students();

-- 3. Каскадное удаление связанных записей при удалении карточки
CREATE OR REPLACE FUNCTION trg_cleanup_on_card_delete() RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM students_cards WHERE card_id = OLD.id;
    DELETE FROM cards_knowledges WHERE card_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_cleanup_on_card_delete ON cards;
CREATE TRIGGER trg_cleanup_on_card_delete
AFTER DELETE ON cards
FOR EACH ROW EXECUTE FUNCTION trg_cleanup_on_card_delete();

-- =====================================
-- Конец файла
-- =====================================
