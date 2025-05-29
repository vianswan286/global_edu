-- Представления (Views)

-- 1. Студенты и их знания (без хеша паролей)
CREATE OR REPLACE VIEW students_knowledge_view AS
SELECT
    s.id AS student_id,
    s.name AS student_name,
    s.email AS student_email,
    k.id AS knowledge_id,
    k.name AS knowledge_name,
    k.description AS knowledge_description,
    sk.quality,
    sk.last_update
FROM students s
LEFT JOIN students_knowledges sk ON sk.student_id = s.id
LEFT JOIN knowledges k ON k.id = sk.knowledge_id
ORDER BY s.name, k.name;

SELECT * FROM students_knowledge_view LIMIT 10;



-- 2. Статистика по курсам - студенты, успешно прошедшие курс и студенты, прошедшие хотя бы одну карточку
CREATE OR REPLACE VIEW course_completion_stats AS
SELECT
    c.id AS course_id,
    c.name AS course_name,
    c.description,
    c.estimated_time,
    (
        -- Количество студентов, успешно прошедших весь курс
        -- Считаем студента успешно прошедшим, если он выполнил все карточки курса
        SELECT COUNT(DISTINCT s.id)
        FROM students s
        WHERE NOT EXISTS (
            SELECT 1
            FROM courses_cards cc
            WHERE cc.course_id = c.id
            AND NOT EXISTS (
                SELECT 1
                FROM students_cards sc
                WHERE sc.card_id = cc.card_id
                AND sc.student_id = s.id
                AND sc.mark IS NOT NULL
            )
        )
        AND EXISTS (
            -- Проверяем, что студент выполнил хотя бы одну карточку курса
            -- (чтобы исключить случаи, когда в курсе нет карточек)
            SELECT 1
            FROM courses_cards cc
            JOIN students_cards sc ON sc.card_id = cc.card_id
            WHERE cc.course_id = c.id
            AND sc.student_id = s.id
            AND sc.mark IS NOT NULL
        )
    ) AS students_completed,
    (
        -- Количество студентов, прошедших хотя бы одну карточку из курса
        SELECT COUNT(DISTINCT sc.student_id)
        FROM students_cards sc
        JOIN courses_cards cc ON cc.card_id = sc.card_id
        WHERE cc.course_id = c.id
        AND sc.mark IS NOT NULL
    ) AS students_started
FROM courses c
ORDER BY c.name;

-- Пример использования:
SELECT * FROM course_completion_stats;


-- Процедура (Procedure)


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
        -- First, check if the student_knowledge exists
        IF NOT EXISTS (SELECT 1 FROM students_knowledges WHERE student_id = p_student_id AND knowledge_id = k_id) THEN
            -- If it doesn't exist, create it
            INSERT INTO students_knowledges (student_id, knowledge_id, quality, last_update)
            VALUES (p_student_id, k_id, p_mark * quality_gain, NOW());
        ELSE
            -- If it exists, update it
            UPDATE students_knowledges sk
            SET quality = LEAST(100, sk.quality + (p_mark * quality_gain)), last_update = NOW()
            WHERE sk.student_id = p_student_id AND sk.knowledge_id = k_id;
        END IF;
    END LOOP;
END;
$$;




-- Функции (Functions)


-- Получить качество знания студента
CREATE OR REPLACE FUNCTION get_student_knowledge(p_student_id INT, p_knowledge_id INT)
RETURNS INT AS $$
    SELECT quality FROM students_knowledges WHERE student_id = p_student_id AND knowledge_id = p_knowledge_id;
$$ LANGUAGE SQL;

SELECT get_student_knowledge(1, 2) AS знание_студента;

-- Получить расчетное время прохождения курса
CREATE OR REPLACE FUNCTION get_course_estimated_time(p_course_id INT)
RETURNS INT AS $$
DECLARE
    total_time INT;
BEGIN
    SELECT COALESCE(SUM(c.time_minutes), 0) INTO total_time
    FROM courses_cards cc
    JOIN cards c ON c.id = cc.card_id
    WHERE cc.course_id = p_course_id;
    RETURN total_time;
END;
$$ LANGUAGE plpgsql;


SELECT get_course_estimated_time(1) AS время_курса_минуты;



-- Триггеры (Triggers)

-- 1. При добавлении карточки в курс связывает курс со знаниями карточки
CREATE OR REPLACE FUNCTION trg_course_card_knowledge_connection() RETURNS TRIGGER AS $$
DECLARE
    k_record RECORD;
BEGIN
    -- Для каждого знания, связанного с добавленной карточкой
    FOR k_record IN 
        SELECT knowledge_id, quality 
        FROM cards_knowledges 
        WHERE card_id = NEW.card_id
    LOOP
        -- Проверяем, существует ли уже связь между курсом и этим знанием
        IF NOT EXISTS (
            SELECT 1 
            FROM courses_final_knowledges 
            WHERE course_id = NEW.course_id AND knowledge_id = k_record.knowledge_id::text
        ) THEN
            -- Если связи нет, создаем новую
            INSERT INTO courses_final_knowledges (course_id, knowledge_id, quality)
            VALUES (NEW.course_id, k_record.knowledge_id::text, k_record.quality);
        ELSE
            -- Если связь существует, обновляем качество, используя максимальное значение
            UPDATE courses_final_knowledges
            SET quality = GREATEST(quality, k_record.quality)
            WHERE course_id = NEW.course_id AND knowledge_id = k_record.knowledge_id::text;
        END IF;
    END LOOP;
    
    -- Обновляем расчетное время прохождения курса
    UPDATE courses
    SET estimated_time = get_course_estimated_time(NEW.course_id)
    WHERE id = NEW.course_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_course_card_knowledge_connection ON courses_cards;
CREATE TRIGGER trg_course_card_knowledge_connection
AFTER INSERT ON courses_cards
FOR EACH ROW
EXECUTE FUNCTION trg_course_card_knowledge_connection();



-- 2. При решении карточки обновляет знания
CREATE OR REPLACE FUNCTION trg_update_knowledge_on_card_mark() RETURNS TRIGGER AS $$
DECLARE
    k_id INT;
    quality_gain INT;
BEGIN
    FOR k_id, quality_gain IN SELECT ck.knowledge_id, ck.quality FROM cards_knowledges ck WHERE ck.card_id = NEW.card_id
    LOOP
        IF NOT EXISTS (SELECT 1 FROM students_knowledges WHERE student_id = NEW.student_id AND knowledge_id = k_id) THEN
            INSERT INTO students_knowledges (student_id, knowledge_id, quality, last_update)
            VALUES (NEW.student_id, k_id, NEW.mark * quality_gain, NOW());
        ELSE
            UPDATE students_knowledges sk
            SET quality = LEAST(100, sk.quality + (NEW.mark * quality_gain)), last_update = NOW()
            WHERE sk.student_id = NEW.student_id AND sk.knowledge_id = k_id;
        END IF;
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
    BEGIN
        INSERT INTO students_cards (student_id, card_id, time)
        SELECT id, NEW.card_id, NOW() FROM students;
    EXCEPTION WHEN unique_violation THEN
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_assign_card_to_all_students ON courses_cards;
CREATE TRIGGER trg_assign_card_to_all_students
AFTER INSERT ON courses_cards
FOR EACH ROW EXECUTE FUNCTION trg_assign_card_to_all_students();



-- 3. Защита от изменения email студента
CREATE OR REPLACE FUNCTION trg_prevent_email_change() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.email <> NEW.email THEN
        NEW.email = OLD.email;
        
        RAISE NOTICE 'Попытка изменить email студента % отклонена. Email остается: %', NEW.name, OLD.email;
    END IF;
        RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_email_change ON students;
CREATE TRIGGER trg_prevent_email_change
BEFORE UPDATE ON students
FOR EACH ROW EXECUTE FUNCTION trg_prevent_email_change();


