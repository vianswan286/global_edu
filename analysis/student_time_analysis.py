#!/usr/bin/env python3
"""
Анализ времени, проведенного студентами на сайте.

График, показывающий для каждого студента промежуток времени между решением первой и последней карточки.
"""

import os
import sys
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Добавляем корневую директорию проекта в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

def connect_to_db():
    """Подключение к базе данных."""
    conn = psycopg2.connect(
        dbname=DB_CONFIG['name'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
    return conn

def get_student_time_data():
    """Получение данных о времени, проведенном студентами на сайте."""
    conn = connect_to_db()
    try:
        # SQL-запрос для получения первой и последней карточки для каждого студента
        query = """
        SELECT 
            s.id AS student_id,
            s.name AS student_name,
            MIN(sc.time) AS first_card_time,
            MAX(sc.time) AS last_card_time,
            MAX(sc.time) - MIN(sc.time) AS time_diff
        FROM 
            students s
        JOIN 
            students_cards sc ON s.id = sc.student_id
        WHERE 
            sc.mark IS NOT NULL
        GROUP BY 
            s.id, s.name
        ORDER BY 
            time_diff DESC
        """
        
        df = pd.read_sql_query(query, conn)
        
        # Вычисляем время, проведенное на сайте (в часах)
        df['time_spent'] = (df['last_card_time'] - df['first_card_time']).apply(
            lambda x: x.total_seconds() / 3600  # Переводим секунды в часы
        )
        
        return df
    finally:
        conn.close()

def format_time_optimal(hours):
    """Форматирование времени в оптимальных единицах."""
    if hours < 0.016:  # Меньше 1 минуты (0.016 часа)
        seconds = hours * 3600
        return f"{seconds:.0f} с"
    elif hours < 1:  # Меньше 1 часа
        minutes = hours * 60
        return f"{minutes:.0f} мин"
    elif hours < 24:  # Меньше 1 дня
        return f"{hours:.1f} ч"
    else:  # Больше 1 дня
        days = hours / 24
        return f"{days:.1f} дней"

def plot_student_time(df):
    """Построение графика времени, проведенного студентами на сайте."""
    # Проверяем корректность данных
    print("\nПроверка данных:")
    print(df[['student_name', 'first_card_time', 'last_card_time', 'time_spent']].head())
    
    # Настраиваем стиль графика
    sns.set_style("whitegrid")
    plt.figure(figsize=(12, 8))
    
    # Создаем порядковые номера для студентов (ось X)
    df['student_index'] = range(1, len(df) + 1)
    
    # Создаем точечный график (только точки, без линий тренда)
    plt.scatter(df['student_index'], df['time_spent'], s=100, alpha=0.7, c='blue')
    
    # Настраиваем заголовки и подписи
    plt.title('Время, проведенное студентами на сайте', fontsize=16)
    plt.xlabel('Студенты (отсортированы по времени на сайте)', fontsize=14)
    plt.ylabel('Время между первой и последней карточкой (часы)', fontsize=14)
    
    # Добавляем сетку
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Настраиваем оси
    plt.xticks(df['student_index'])
    
    # Добавляем аннотации с именами студентов и временем в оптимальных единицах
    for i, row in df.iterrows():
        formatted_time = format_time_optimal(row['time_spent'])
        plt.annotate(f"{row['student_name']} ({formatted_time})", 
                    (row['student_index'], row['time_spent']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=9, alpha=0.9)
    
    plt.tight_layout()
    
    # Сохраняем график
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'student_time_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"График сохранен в: {output_path}")
    
    # Показываем график
    plt.show()

def main():
    """Основная функция анализа."""
    print("Анализ времени, проведенного студентами на сайте")
    print("-" * 60)
    
    # Получаем данные
    df = get_student_time_data()
    
    if df.empty:
        print("Нет данных о времени, проведенном студентами на сайте.")
        return
    
    # Выводим информацию о студентах
    print("Информация о времени, проведенном студентами на сайте:")
    for i, row in df.iterrows():
        print(f"Студент: {row['student_name']}")
        print(f"Первая карточка: {row['first_card_time']}")
        print(f"Последняя карточка: {row['last_card_time']}")
        print(f"Время на сайте: {row['time_spent']:.2f} часов")
        print("-" * 40)
    
    # Строим график
    plot_student_time(df)

if __name__ == "__main__":
    main()
