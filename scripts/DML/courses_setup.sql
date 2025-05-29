-- Configure course structure with 5 courses, each with 10 cards
-- This script ensures we have consistent course and card data in the database

-- First, create 5 well-defined courses if they don't exist yet
INSERT INTO courses (name, description, estimated_time)
VALUES 
  ('Базовая арифметика', 'Основные арифметические операции: сложение, вычитание, умножение, деление и дроби', 120),
  ('Введение в алгебру', 'Базовые алгебраические концепции: уравнения, функции и выражения', 150),
  ('Геометрия и измерения', 'Фигуры, теоремы и формулы для вычисления площадей и объёмов', 150),
  ('Тригонометрия и геометрия', 'Синусы, косинусы, тангенсы и их применение в геометрии', 180),
  ('Продвинутая математика', 'Комплексный курс включающий элементы анализа, статистики и высшей математики', 200);
-- Note: We can't use ON CONFLICT (name) since there might not be a unique constraint on name

-- Create a new set of cards for each course to ensure we have consistent data
-- Arithmetic cards (10)
INSERT INTO cards (question, answer, time_minutes)
VALUES
  ('Что такое сложение?', 'Сложение - это арифметическая операция, объединяющая два числа в одно.', 2),
  ('Как найти НОД двух чисел?', 'Для нахождения наибольшего общего делителя можно использовать алгоритм Евклида.', 3),
  ('Что такое дробь?', 'Дробь - это число, представляющее часть целого. Записывается как отношение двух чисел.', 2),
  ('Как сложить дроби с разными знаменателями?', 'Нужно привести дроби к общему знаменателю, а затем сложить числители.', 2),
  ('Как умножить две дроби?', 'При умножении дробей нужно умножить числитель на числитель, а знаменатель на знаменатель.', 1),
  ('Что такое деление?', 'Деление - это математическая операция, обратная умножению. Находит, сколько раз одно число содержится в другом.', 2),
  ('Как вычислить процент от числа?', 'Чтобы найти X% от числа Y, нужно умножить Y на X и разделить на 100.', 2),
  ('Что такое десятичная дробь?', 'Десятичная дробь - способ записи дробных чисел с использованием десятичной системы счисления.', 2),
  ('Как округлить число?', 'При округлении до определенного разряда: если следующая цифра ≥ 5, разряд увеличивается на 1, иначе не меняется.', 1),
  ('Что такое отрицательное число?', 'Отрицательное число - это число, которое меньше нуля и находится слева от нуля на числовой прямой.', 2);

-- Algebra cards (10)
INSERT INTO cards (question, answer, time_minutes)
VALUES
  ('Что такое линейное уравнение?', 'Линейное уравнение - это уравнение вида ax + b = 0, где x - неизвестная, a и b - константы, a ≠ 0.', 3),
  ('Как решить квадратное уравнение?', 'Квадратное уравнение ax² + bx + c = 0 можно решить по формуле: x = (-b ± √(b² - 4ac)) / 2a', 4),
  ('Что такое функция?', 'Функция - это правило, которое каждому значению из множества X ставит в соответствие ровно одно значение из множества Y.', 2),
  ('Что такое график функции?', 'График функции - это множество точек на координатной плоскости, соответствующих всем парам значений (x, f(x)).', 2),
  ('Как найти корни многочлена?', 'Корни многочлена можно найти разными способами: разложением на множители, методом группировки, или формулами.', 3),
  ('Что такое система уравнений?', 'Система уравнений - набор уравнений с общими переменными, для которых требуется найти значения, удовлетворяющие всем уравнениям одновременно.', 3),
  ('Что такое неравенство?', 'Неравенство - математическое выражение, показывающее отношение "больше" или "меньше" между двумя величинами.', 2),
  ('Как решить систему линейных уравнений?', 'Систему линейных уравнений можно решить методами подстановки, сложения или методом Гаусса.', 4),
  ('Что такое область определения функции?', 'Область определения - множество всех допустимых значений аргумента, при которых функция имеет смысл.', 3),
  ('Что такое квадратичная функция?', 'Квадратичная функция имеет вид f(x) = ax² + bx + c, где a ≠ 0. Её графиком является парабола.', 2)
ON CONFLICT (question) DO UPDATE 
  SET answer = EXCLUDED.answer, 
      time_minutes = EXCLUDED.time_minutes;

-- Geometry cards (10)
INSERT INTO cards (question, answer, time_minutes)
VALUES
  ('Что такое окружность?', 'Окружность - это множество точек на плоскости, равноудаленных от заданной точки (центра).', 2),
  ('Что такое теорема Пифагора?', 'В прямоугольном треугольнике квадрат гипотенузы равен сумме квадратов катетов: a² + b² = c².', 3),
  ('Как найти площадь треугольника?', 'Площадь треугольника можно найти по формуле S = (1/2) × основание × высота или по формуле Герона.', 2),
  ('Что такое параллелограмм?', 'Параллелограмм - это четырехугольник, у которого противоположные стороны параллельны и равны.', 1),
  ('Как найти площадь круга?', 'Площадь круга вычисляется по формуле S = πr², где r - радиус круга.', 1),
  ('Как найти объем пирамиды?', 'Объем пирамиды равен V = (1/3) × площадь основания × высота.', 2),
  ('Что такое подобные треугольники?', 'Подобные треугольники имеют соответственно равные углы и пропорциональные стороны.', 3),
  ('Как найти длину окружности?', 'Длина окружности вычисляется по формуле L = 2πr, где r - радиус окружности.', 1),
  ('Что такое медиана треугольника?', 'Медиана треугольника - отрезок, соединяющий вершину треугольника с серединой противоположной стороны.', 2),
  ('Что такое вписанная и описанная окружности?', 'Вписанная окружность касается всех сторон многоугольника. Описанная окружность проходит через все вершины многоугольника.', 3)
ON CONFLICT (question) DO UPDATE 
  SET answer = EXCLUDED.answer, 
      time_minutes = EXCLUDED.time_minutes;

-- Trigonometry cards (10)
INSERT INTO cards (question, answer, time_minutes)
VALUES
  ('Что такое синус?', 'Синус угла в прямоугольном треугольнике - это отношение противолежащего катета к гипотенузе.', 2),
  ('Что такое косинус?', 'Косинус угла в прямоугольном треугольнике - это отношение прилежащего катета к гипотенузе.', 2),
  ('Чему равен синус 30 градусов?', 'Синус 30 градусов равен 1/2.', 1),
  ('Что такое тангенс?', 'Тангенс угла в прямоугольном треугольнике - это отношение противолежащего катета к прилежащему, также равен sin(α)/cos(α).', 2),
  ('Какова связь между синусом и косинусом?', 'Основное тригонометрическое тождество: sin²α + cos²α = 1.', 2),
  ('Что такое котангенс?', 'Котангенс угла - это отношение прилежащего катета к противолежащему, также равен cos(α)/sin(α) или 1/tg(α).', 2),
  ('Как перевести градусы в радианы?', 'Чтобы перевести градусы в радианы, нужно умножить градусы на π/180.', 1),
  ('Чему равен косинус 60 градусов?', 'Косинус 60 градусов равен 1/2.', 1),
  ('Что такое единичная окружность в тригонометрии?', 'Единичная окружность - окружность с радиусом 1 и центром в начале координат, используемая для определения тригонометрических функций.', 3),
  ('Как найти синус суммы двух углов?', 'Sin(α+β) = sin(α)cos(β) + cos(α)sin(β).', 2)
ON CONFLICT (question) DO UPDATE 
  SET answer = EXCLUDED.answer, 
      time_minutes = EXCLUDED.time_minutes;

-- Advanced math cards (10)
INSERT INTO cards (question, answer, time_minutes)
VALUES
  ('Что такое производная функции?', 'Производная функции - это скорость изменения функции в точке, обозначается f''(x).', 4),
  ('Что такое интеграл функции?', 'Интеграл функции - это площадь под графиком функции, обозначается ∫f(x)dx.', 4),
  ('Что такое предел функции?', 'Предел функции - это значение, к которому стремится функция при приближении аргумента к заданному числу.', 3),
  ('Что такое вектор?', 'Вектор - это направленный отрезок, имеющий величину и направление.', 2),
  ('Что такое матрица?', 'Матрица - это прямоугольная таблица чисел, используемая в линейной алгебре.', 2),
  ('Что такое комплексное число?', 'Комплексное число - это число вида a + bi, где a и b - действительные числа, а i - мнимая единица.', 3),
  ('Что такое дифференциальное уравнение?', 'Дифференциальное уравнение - это уравнение, содержащее производные неизвестной функции.', 4),
  ('Что такое вероятность?', 'Вероятность - это численная мера возможности наступления случайного события.', 2),
  ('Что такое математическая индукция?', 'Математическая индукция - метод доказательства, утверждающий справедливость бесконечного числа предложений.', 3),
  ('Что такое ряд Тейлора?', 'Ряд Тейлора - представление функции в виде бесконечной суммы слагаемых, вычисленных из значений производных функции в одной точке.', 4)
ON CONFLICT (question) DO UPDATE 
  SET answer = EXCLUDED.answer, 
      time_minutes = EXCLUDED.time_minutes;

-- Link cards to the appropriate courses
-- Clear existing links to ensure consistency
DELETE FROM courses_cards;

-- Link Arithmetic course
WITH arithmetic_course AS (SELECT id FROM courses WHERE name = 'Базовая арифметика'),
     arithmetic_cards AS (SELECT id FROM cards WHERE question IN 
      ('Что такое сложение?', 'Как найти НОД двух чисел?', 'Что такое дробь?', 
       'Как сложить дроби с разными знаменателями?', 'Как умножить две дроби?',
       'Что такое деление?', 'Как вычислить процент от числа?', 'Что такое десятичная дробь?',
       'Как округлить число?', 'Что такое отрицательное число?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT ac.id, arc.id
FROM arithmetic_course ac, arithmetic_cards arc
ON CONFLICT DO NOTHING;

-- Link Algebra course
WITH algebra_course AS (SELECT id FROM courses WHERE name = 'Введение в алгебру'),
     algebra_cards AS (SELECT id FROM cards WHERE question IN 
      ('Что такое линейное уравнение?', 'Как решить квадратное уравнение?', 'Что такое функция?', 
       'Что такое график функции?', 'Как найти корни многочлена?', 'Что такое система уравнений?',
       'Что такое неравенство?', 'Как решить систему линейных уравнений?', 
       'Что такое область определения функции?', 'Что такое квадратичная функция?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT ac.id, alc.id
FROM algebra_course ac, algebra_cards alc
ON CONFLICT DO NOTHING;

-- Link Geometry course
WITH geometry_course AS (SELECT id FROM courses WHERE name = 'Геометрия и измерения'),
     geometry_cards AS (SELECT id FROM cards WHERE question IN 
      ('Что такое окружность?', 'Что такое теорема Пифагора?', 'Как найти площадь треугольника?', 
       'Что такое параллелограмм?', 'Как найти площадь круга?', 'Как найти объем пирамиды?',
       'Что такое подобные треугольники?', 'Как найти длину окружности?', 
       'Что такое медиана треугольника?', 'Что такое вписанная и описанная окружности?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT gc.id, gec.id
FROM geometry_course gc, geometry_cards gec
ON CONFLICT DO NOTHING;

-- Link Trigonometry course
WITH trig_course AS (SELECT id FROM courses WHERE name = 'Тригонометрия и геометрия'),
     trig_cards AS (SELECT id FROM cards WHERE question IN 
      ('Что такое синус?', 'Что такое косинус?', 'Чему равен синус 30 градусов?',
       'Что такое тангенс?', 'Какова связь между синусом и косинусом?', 'Что такое котангенс?',
       'Как перевести градусы в радианы?', 'Чему равен косинус 60 градусов?', 
       'Что такое единичная окружность в тригонометрии?', 'Как найти синус суммы двух углов?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT tc.id, trc.id
FROM trig_course tc, trig_cards trc
ON CONFLICT DO NOTHING;

-- Link Advanced Math course
WITH adv_course AS (SELECT id FROM courses WHERE name = 'Продвинутая математика'),
     adv_cards AS (SELECT id FROM cards WHERE question IN 
      ('Что такое производная функции?', 'Что такое интеграл функции?', 'Что такое предел функции?',
       'Что такое вектор?', 'Что такое матрица?', 'Что такое комплексное число?', 
       'Что такое дифференциальное уравнение?', 'Что такое вероятность?', 
       'Что такое математическая индукция?', 'Что такое ряд Тейлора?'))
INSERT INTO courses_cards (course_id, card_id)
SELECT adc.id, avc.id
FROM adv_course adc, adv_cards avc
ON CONFLICT DO NOTHING;

-- Link all cards to appropriate knowledge units based on their content
DO $$
DECLARE
    card_id INTEGER;
    knowledge_id INTEGER;
BEGIN
    -- Link each card to at least one knowledge unit
    -- We'll try to match by keywords in the card question and knowledge name/description
    
    -- ARITHMETIC CARDS
    -- Сложение
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%сложение%' OR name LIKE '%операц%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое сложение?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 25)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;

    -- НОД
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%делитель%' OR name LIKE '%НОД%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как найти НОД двух чисел?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 30)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;

    -- Дробь
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%дроб%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое дробь?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 20)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;

    -- Сложение дробей
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%сложение%' OR name LIKE '%дроб%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как сложить дроби с разными знаменателями?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 25)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;

    -- Умножение дробей
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%умножение%' OR name LIKE '%дроб%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как умножить две дроби?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 20)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;

    -- Деление
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%делени%' OR name LIKE '%операц%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое деление?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 20)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;

    -- Процент
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%процент%' OR name LIKE '%дроб%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как вычислить процент от числа?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 15)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;

    -- ALGEBRA CARDS
    -- Линейное уравнение
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%уравнени%' OR name LIKE '%алгебр%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Что такое линейное уравнение?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 25)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;

    -- Квадратное уравнение
    SELECT id INTO knowledge_id FROM knowledges WHERE name LIKE '%квадратн%' OR name LIKE '%уравнени%' LIMIT 1;
    IF knowledge_id IS NOT NULL THEN
        SELECT id INTO card_id FROM cards WHERE question = 'Как решить квадратное уравнение?';
        IF card_id IS NOT NULL THEN
            INSERT INTO cards_knowledges (card_id, knowledge_id, quality) VALUES (card_id, knowledge_id, 35)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;

    -- Ensure all cards have at least one knowledge linked
    -- Create a generic math knowledge to use as fallback
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
            SELECT generic_math_id, id FROM collections WHERE name LIKE '%Арифметика%' LIMIT 1;
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

-- Update all course times based on their cards
SELECT update_all_courses_time();
