-- Добавление коллекций знаний согласно основным разделам

-- Using DO block to conditionally insert collections only if they don't exist
DO $$
DECLARE
    collection_names TEXT[] := ARRAY[
        'Арифметика и основы числовой системы', 
        'Алгебра', 
        'Геометрия и измерения', 
        'Тригонометрия', 
        'Анализ данных, статистика и вероятность', 
        'Предварительный анализ', 
        'Дифференциальное и интегральное исчисление', 
        'Линейная алгебра'
    ];
    collection_descriptions TEXT[] := ARRAY[
        'Базовые знания о числовых системах, основных арифметических операциях, дробях и элементарной теории чисел.',
        'Основы алгебры: выражения, уравнения, неравенства, функции и системы уравнений.',
        'Евклидова геометрия, координатная геометрия, измерения фигур, периметр, площадь и объем.',
        'Изучение тригонометрических функций, единичной окружности, графиков и тригонометрических тождеств.',
        'Основы описательной статистики, представления данных, вероятностных моделей и комбинаторики.',
        'Изучение продвинутых функций, последовательностей, рядов и введение в понятие предела как подготовка к исчислению.',
        'Введение в понятие пределов, производных, интегралов и фундаментальную теорему анализа.',
        'Векторы, матрицы, системы линейных уравнений, понятие векторных пространств.'
    ];
    start_id INT := 100; -- Start with a high ID to avoid conflicts
    i INT;
    existing_count INT;
    current_name TEXT;
    current_description TEXT;
BEGIN
    -- Loop through collection names and conditionally insert them
    FOR i IN 1..array_length(collection_names, 1) LOOP
        current_name := collection_names[i];
        current_description := collection_descriptions[i];
        
        -- Check if this collection name already exists
        SELECT COUNT(*) INTO existing_count FROM collections WHERE name = current_name;
        
        IF existing_count = 0 THEN
            -- Only insert if the collection doesn't exist
            INSERT INTO collections (id, name, description) 
            VALUES (start_id + i, current_name, current_description);
            RAISE NOTICE 'Inserted collection: %', current_name;
        ELSE
            RAISE NOTICE 'Collection already exists: %', current_name;
        END IF;
    END LOOP;
END;
$$;

-- Additional collections
DO $$
DECLARE
    more_collection_names TEXT[] := ARRAY[
        'Дифференциальные уравнения', 
        'Введение в математические доказательства и дискретную математику', 
        'Дополнительные темы'
    ];
    more_collection_descriptions TEXT[] := ARRAY[
        'Введение в обыкновенные дифференциальные уравнения, методы их решения и моделирование динамических систем.',
        'Логика, методы доказательства, основы теории множеств, комбинаторика и элементарная графовая теория.',
        'Расширенные концепции: комплексные числа, основы топологии и нестандартные задачи для развития творческого мышления.'
    ];
    start_id INT := 200; -- Start with a higher ID to avoid conflicts
    i INT;
    existing_count INT;
    current_name TEXT;
    current_description TEXT;
BEGIN
    -- Loop through collection names and conditionally insert them
    FOR i IN 1..array_length(more_collection_names, 1) LOOP
        current_name := more_collection_names[i];
        current_description := more_collection_descriptions[i];
        
        -- Check if this collection name already exists
        SELECT COUNT(*) INTO existing_count FROM collections WHERE name = current_name;
        
        IF existing_count = 0 THEN
            -- Only insert if the collection doesn't exist
            INSERT INTO collections (id, name, description) 
            VALUES (start_id + i, current_name, current_description);
            RAISE NOTICE 'Inserted collection: %', current_name;
        ELSE
            RAISE NOTICE 'Collection already exists: %', current_name;
        END IF;
    END LOOP;
END;
$$;
