#!/usr/bin/env python3
"""
Анализ числа студентов, начавших каждый курс.

Диаграмма, показывающая количество студентов, начавших каждый из курсов.
"""

import os
import sys
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

def get_course_data():
    """Получение данных о курсах из представления course_completion_stats."""
    conn = connect_to_db()
    try:
        # Используем pandas для удобного анализа данных
        df = pd.read_sql_query("SELECT course_id, course_name, estimated_time, students_started FROM course_completion_stats", conn)
        return df
    finally:
        conn.close()

def plot_course_enrollment(df):
    """Построение диаграммы числа студентов, начавших каждый курс."""
    # Настраиваем стиль графика
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 6))
    
    # Сортируем курсы по числу начавших студентов (от большего к меньшему)
    df = df.sort_values('students_started', ascending=False)
    
    # Создаем столбчатую диаграмму с числом начавших студентов
    ax = sns.barplot(x='course_name', y='students_started', data=df, palette='viridis')
    
    # Настраиваем заголовки и подписи
    plt.title('Число студентов, начавших каждый курс', fontsize=16)
    plt.xlabel('Название курса (продолжительность в минутах)', fontsize=14)
    plt.ylabel('Количество студентов', fontsize=14)
    
    # Добавляем значения над столбцами
    for i, row in df.iterrows():
        plt.text(i, row['students_started'] + 0.1, str(row['students_started']), 
                ha='center', va='bottom', fontsize=12)
    
    # Создаем подписи с названием курса и продолжительностью
    labels = [f"{row['course_name']}\n({row['estimated_time']} мин)" for _, row in df.iterrows()]
    plt.xticks(range(len(labels)), labels, rotation=0)
    
    plt.tight_layout()
    
    # Сохраняем график
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'course_enrollment_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"График сохранен в: {output_path}")
    
    # Показываем график
    plt.show()

def main():
    """Основная функция анализа."""
    print("Анализ числа студентов, начавших каждый курс")
    print("-" * 50)
    
    # Получаем данные
    df = get_course_data()
    
    if df.empty:
        print("Нет данных о курсах.")
        return
    
    # Выводим информацию о курсах
    print("Информация о курсах:")
    for i, row in df.iterrows():
        print(f"Курс: {row['course_name']}, Продолжительность: {row['estimated_time']} минут")
        print(f"Начали: {row['students_started']} студентов")
        print("-" * 30)
    
    # Строим диаграмму
    plot_course_enrollment(df)

if __name__ == "__main__":
    main()
