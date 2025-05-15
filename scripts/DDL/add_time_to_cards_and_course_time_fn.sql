-- 1. Добавить поле времени к карточкам (если его ещё нет)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.columns 
                  WHERE table_name = 'cards' AND column_name = 'time_minutes') THEN
        ALTER TABLE cards ADD COLUMN time_minutes INTEGER DEFAULT 5;
    END IF;
END $$;

-- 2. Добавить поле времени к курсам
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.columns 
                  WHERE table_name = 'courses' AND column_name = 'estimated_time') THEN
        ALTER TABLE courses ADD COLUMN estimated_time INTEGER DEFAULT 0;
    END IF;
END $$;

-- 3. Функция для расчета времени курса как суммы времени всех карточек
CREATE OR REPLACE FUNCTION get_course_estimated_time(p_course_id INT)
RETURNS INTEGER AS $$
    SELECT COALESCE(SUM(c.time_minutes), 0)
    FROM courses_cards cc
    JOIN cards c ON c.id = cc.card_id
    WHERE cc.course_id = p_course_id;
$$ LANGUAGE SQL;

-- 4. Триггер для автоматического обновления времени курса при добавлении/удалении карточек
CREATE OR REPLACE FUNCTION trg_update_course_time() RETURNS TRIGGER AS $$
DECLARE
    target_course_id INTEGER;
BEGIN
    IF TG_OP = 'DELETE' THEN
        target_course_id := OLD.course_id;
    ELSE
        target_course_id := NEW.course_id;
    END IF;
    
    UPDATE courses 
    SET estimated_time = get_course_estimated_time(target_course_id)
    WHERE id = target_course_id;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 5. Создать триггер для courses_cards
DROP TRIGGER IF EXISTS trg_update_course_time ON courses_cards;
CREATE TRIGGER trg_update_course_time
AFTER INSERT OR DELETE OR UPDATE ON courses_cards
FOR EACH ROW EXECUTE FUNCTION trg_update_course_time();

-- 6. Функция для обновления времени всех курсов
CREATE OR REPLACE FUNCTION update_all_courses_time() RETURNS VOID AS $$
DECLARE
    course_record RECORD;
BEGIN
    FOR course_record IN SELECT id FROM courses LOOP
        UPDATE courses 
        SET estimated_time = get_course_estimated_time(course_record.id)
        WHERE id = course_record.id;
    END LOOP;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;
