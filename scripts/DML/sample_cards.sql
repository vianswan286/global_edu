-- Sample cards for courses
-- This script adds sample cards to each course and links them properly to knowledge units

-- First, create sample cards for different knowledge areas
INSERT INTO cards (question, answer, time_minutes) VALUES
-- Arithmetic cards
('Что такое сложение?', 'Сложение - это арифметическая операция, объединяющая два числа в одно.', 2),
('Как найти НОД двух чисел?', 'Для нахождения наибольшего общего делителя можно использовать алгоритм Евклида.', 3),
('Что такое дробь?', 'Дробь - это число, представляющее часть целого. Записывается как отношение двух чисел.', 2),
('Как сложить дроби с разными знаменателями?', 'Нужно привести дроби к общему знаменателю, а затем сложить числители.', 2),
('Как умножить две дроби?', 'При умножении дробей нужно умножить числитель на числитель, а знаменатель на знаменатель.', 1),

-- Algebra cards
('Что такое линейное уравнение?', 'Линейное уравнение - это уравнение, содержащее переменную в первой степени: ax + b = 0.', 3),
('Как решить квадратное уравнение?', 'Квадратное уравнение ax² + bx + c = 0 можно решить по формуле: x = (-b ± √(b² - 4ac)) / 2a', 4),
('Что такое функция?', 'Функция - это правило, которое каждому значению из множества X ставит в соответствие ровно одно значение из множества Y.', 2),
('Что такое график функции?', 'График функции - это множество точек на координатной плоскости, соответствующих всем парам значений (x, f(x)).', 2),
('Как найти корни многочлена?', 'Корни многочлена можно найти разными способами: разложением на множители, методом группировки, или с помощью формул для квадратных уравнений.', 3),

-- Geometry cards
('Что такое окружность?', 'Окружность - это множество точек на плоскости, равноудаленных от заданной точки (центра).', 2),
('Что такое теорема Пифагора?', 'В прямоугольном треугольнике квадрат гипотенузы равен сумме квадратов катетов: a² + b² = c².', 3),
('Как найти площадь треугольника?', 'Площадь треугольника можно найти по формуле S = (1/2) × основание × высота или по формуле Герона.', 2),
('Что такое параллелограмм?', 'Параллелограмм - это четырехугольник, у которого противоположные стороны параллельны и равны.', 1),
('Как найти площадь круга?', 'Площадь круга вычисляется по формуле S = πr², где r - радиус круга.', 1),

-- Trigonometry cards
('Что такое синус?', 'Синус угла в прямоугольном треугольнике - это отношение противолежащего катета к гипотенузе.', 2),
('Что такое косинус?', 'Косинус угла в прямоугольном треугольнике - это отношение прилежащего катета к гипотенузе.', 2),
('Чему равен синус 30 градусов?', 'Синус 30 градусов равен 1/2.', 1),
('Что такое тангенс?', 'Тангенс угла в прямоугольном треугольнике - это отношение противолежащего катета к прилежащему.', 2),
('Какова связь между синусом и косинусом?', 'Основное тригонометрическое тождество: sin²α + cos²α = 1.', 2);

-- Link cards to courses based on the course names
-- For Базовая арифметика
WITH arithmetic_course AS (SELECT id FROM courses WHERE name = 'Базовая арифметика'),
     arithmetic_cards AS (SELECT id FROM cards WHERE question IN 
                         ('Что такое сложение?', 'Как найти НОД двух чисел?', 'Что такое дробь?',
                          'Как сложить дроби с разными знаменателями?', 'Как умножить две дроби?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT ac.id, arc.id
FROM arithmetic_course ac, arithmetic_cards arc
ON CONFLICT DO NOTHING;

-- For Основы алгебры
WITH algebra_course AS (SELECT id FROM courses WHERE name = 'Основы алгебры'),
     algebra_cards AS (SELECT id FROM cards WHERE question IN 
                      ('Что такое линейное уравнение?', 'Как решить квадратное уравнение?', 'Что такое функция?',
                       'Что такое график функции?', 'Как найти корни многочлена?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT ac.id, alc.id
FROM algebra_course ac, algebra_cards alc
ON CONFLICT DO NOTHING;

-- For Геометрия и измерения
WITH geometry_course AS (SELECT id FROM courses WHERE name = 'Геометрия и измерения'),
     geometry_cards AS (SELECT id FROM cards WHERE question IN 
                       ('Что такое окружность?', 'Что такое теорема Пифагора?', 'Как найти площадь треугольника?',
                        'Что такое параллелограмм?', 'Как найти площадь круга?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT gc.id, geoc.id
FROM geometry_course gc, geometry_cards geoc
ON CONFLICT DO NOTHING;

-- For Тригонометрия и геометрия
WITH trig_course AS (SELECT id FROM courses WHERE name = 'Тригонометрия и геометрия'),
     trig_cards AS (SELECT id FROM cards WHERE question IN 
                   ('Что такое синус?', 'Что такое косинус?', 'Чему равен синус 30 градусов?',
                    'Что такое тангенс?', 'Какова связь между синусом и косинусом?'))
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
    -- Link new addition cards
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%сложение дробей%' OR name LIKE '%дроб%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как сложить дроби с разными знаменателями?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 20)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Link multiplication of fractions
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%умножение дробей%' OR name LIKE '%дроб%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как умножить две дроби?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 15)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Link function graph
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%функци%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое график функции?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 18)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Link polynomial roots
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%уравнени%' OR name LIKE '%корни%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как найти корни многочлена?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 22)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Link parallelogram
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%геометри%' OR name LIKE '%фигур%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое параллелограмм?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 15)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Link circle area
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%круг%' OR name LIKE '%окружност%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как найти площадь круга?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 12)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Link tangent
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%тригонометр%' OR name LIKE '%синус%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое тангенс?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 18)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Link trigonometric identity
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%тригонометр%' OR name LIKE '%синус%косинус%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Какова связь между синусом и косинусом?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 20)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    -- Make sure we have at least one knowledge linked to each card
    -- Define a generic knowledge unit for fallback
    DECLARE
        generic_math_id INTEGER;
    BEGIN
        -- Get or create a generic math knowledge
        SELECT id INTO generic_math_id FROM knowledges WHERE name = 'Базовая математика' LIMIT 1;
        IF generic_math_id IS NULL THEN
            INSERT INTO knowledges (name, theory, description)
            VALUES ('Базовая математика', 'Основы математических вычислений и концепций', 'Основные математические принципы')
            RETURNING id INTO generic_math_id;
            
            -- Link to appropriate collection
            INSERT INTO knowledges_collections (knowledge_id, collection_id)
            SELECT generic_math_id, id FROM collections WHERE name = 'Арифметика' LIMIT 1;
        END IF;
        
        -- Link all cards that don't have a knowledge association to this generic knowledge
        FOR card_id IN
            SELECT c.id FROM cards c
            LEFT JOIN cards_knowledges ck ON ck.card_id = c.id
            WHERE ck.id IS NULL
        LOOP
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality)
            VALUES (card_id, generic_math_id, 10)
            ON CONFLICT DO NOTHING;
        END LOOP;
    END;
END;
$$;

-- Update all course times now that we've added cards
SELECT update_all_courses_time();
