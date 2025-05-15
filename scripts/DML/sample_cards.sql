-- Sample cards for courses
-- This script adds sample cards to each course and links them properly to knowledge units

-- First, create sample cards for different knowledge areas
INSERT INTO cards (question, answer, time_minutes) VALUES
-- Arithmetic cards
('Что такое сложение?', 'Сложение - это арифметическая операция, объединяющая два числа в одно.', 5),
('Как найти НОД двух чисел?', 'Для нахождения наибольшего общего делителя можно использовать алгоритм Евклида.', 7),
('Что такое дробь?', 'Дробь - это число, представляющее часть целого. Записывается как отношение двух чисел.', 6),

-- Algebra cards
('Что такое линейное уравнение?', 'Линейное уравнение - это уравнение, содержащее переменную в первой степени: ax + b = 0.', 8),
('Как решить квадратное уравнение?', 'Квадратное уравнение ax² + bx + c = 0 можно решить по формуле: x = (-b ± √(b² - 4ac)) / 2a', 10),
('Что такое функция?', 'Функция - это правило, которое каждому значению из множества X ставит в соответствие ровно одно значение из множества Y.', 7),

-- Geometry cards
('Что такое окружность?', 'Окружность - это множество точек на плоскости, равноудаленных от заданной точки (центра).', 5),
('Что такое теорема Пифагора?', 'В прямоугольном треугольнике квадрат гипотенузы равен сумме квадратов катетов: a² + b² = c².', 8),
('Как найти площадь треугольника?', 'Площадь треугольника можно найти по формуле S = (1/2) × основание × высота или по формуле Герона.', 7),

-- Trigonometry cards
('Что такое синус?', 'Синус угла в прямоугольном треугольнике - это отношение противолежащего катета к гипотенузе.', 7),
('Что такое косинус?', 'Косинус угла в прямоугольном треугольнике - это отношение прилежащего катета к гипотенузе.', 7),
('Чему равен синус 30 градусов?', 'Синус 30 градусов равен 1/2.', 4);

-- Link cards to courses based on the course names
-- For Базовая арифметика
WITH arithmetic_course AS (SELECT id FROM courses WHERE name = 'Базовая арифметика'),
     arithmetic_cards AS (SELECT id FROM cards WHERE question IN 
                         ('Что такое сложение?', 'Как найти НОД двух чисел?', 'Что такое дробь?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT ac.id, arc.id
FROM arithmetic_course ac, arithmetic_cards arc
ON CONFLICT DO NOTHING;

-- For Основы алгебры
WITH algebra_course AS (SELECT id FROM courses WHERE name = 'Основы алгебры'),
     algebra_cards AS (SELECT id FROM cards WHERE question IN 
                      ('Что такое линейное уравнение?', 'Как решить квадратное уравнение?', 'Что такое функция?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT ac.id, alc.id
FROM algebra_course ac, algebra_cards alc
ON CONFLICT DO NOTHING;

-- For Геометрия и измерения
WITH geometry_course AS (SELECT id FROM courses WHERE name = 'Геометрия и измерения'),
     geometry_cards AS (SELECT id FROM cards WHERE question IN 
                       ('Что такое окружность?', 'Что такое теорема Пифагора?', 'Как найти площадь треугольника?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT gc.id, geoc.id
FROM geometry_course gc, geometry_cards geoc
ON CONFLICT DO NOTHING;

-- For Тригонометрия и геометрия
WITH trig_course AS (SELECT id FROM courses WHERE name = 'Тригонометрия и геометрия'),
     trig_cards AS (SELECT id FROM cards WHERE question IN 
                   ('Что такое синус?', 'Что такое косинус?', 'Чему равен синус 30 градусов?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT tc.id, trigc.id
FROM trig_course tc, trig_cards trigc
ON CONFLICT DO NOTHING;

-- Link cards to knowledges
-- Find knowledges by name pattern and link cards
DO $$
DECLARE
    knowledge_id INTEGER;
    card_id INTEGER;
BEGIN
    -- Arithmetic operations
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%сложение%' OR name LIKE '%арифметические операци%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое сложение?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 25)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- НОД GCD
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%наибольш%общий делитель%' OR name LIKE '%НОД%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как найти НОД двух чисел?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 30)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Fractions
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%дроб%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое дробь?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 20)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Linear equations
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%линейное уравнение%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое линейное уравнение?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 25)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Quadratic equations
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%квадратн%уравнени%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как решить квадратное уравнение?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 35)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Functions
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%функци%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое функция?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 25)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Circle
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%окружност%' OR name LIKE '%круг%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое окружность?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 20)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Pythagorean theorem
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%Пифагор%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое теорема Пифагора?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 30)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Triangle area
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%площад%треугольник%' OR name LIKE '%треугольник%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как найти площадь треугольника?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 25)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Sine
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%синус%' OR name LIKE '%тригонометр%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое синус?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 30)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Cosine
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%косинус%' OR name LIKE '%тригонометр%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое косинус?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 30)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Sine 30
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%cинус%' OR name LIKE '%тригонометр%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Чему равен синус 30 градусов?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 15)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
END;
$$;

-- Update all course times now that we've added cards
SELECT update_all_courses_time();
