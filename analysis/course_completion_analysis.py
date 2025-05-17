#!/usr/bin/env python3
"""
Анализ завершения курсов.

Диаграмма, показывающая долю студентов, завершивших курс, с указанием продолжительности курса.
"""

import os
import sys
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter

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
        df = pd.read_sql_query("SELECT course_id, course_name, estimated_time, students_completed, students_started FROM course_completion_stats", conn)
        return df
    finally:
        conn.close()

def plot_course_completion(df):
    """Построение диаграммы доли завершивших курс."""
    # Вычисляем долю завершивших среди начавших
    df['completion_rate'] = df.apply(
        lambda row: row['students_completed'] / row['students_started'] if row['students_started'] > 0 else 0, 
        axis=1
    )
    
    # Настраиваем стиль графика
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 6))
    
    # Создаем столбчатую диаграмму с долей завершивших
    ax = sns.barplot(x='course_name', y='completion_rate', data=df, palette='viridis')
    
    # Настраиваем заголовки и подписи
    plt.title('Доля студентов, завершивших курс', fontsize=16)
    plt.xlabel('Название курса (продолжительность в минутах)', fontsize=14)
    plt.ylabel('Доля завершивших среди начавших', fontsize=14)
    
    # Форматируем ось Y как проценты
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
    
    # Добавляем значения процентов над столбцами
    for i, row in df.iterrows():
        plt.text(i, row['completion_rate'] + 0.02, f"{row['completion_rate']:.1%}", 
                ha='center', va='bottom', fontsize=12)
    
    # Создаем подписи с названием курса и продолжительностью
    labels = [f"{row['course_name']}\n({row['estimated_time']} мин)" for _, row in df.iterrows()]
    plt.xticks(range(len(labels)), labels, rotation=0)
    
    plt.tight_layout()
    
    # Сохраняем график
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'course_completion_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"График сохранен в: {output_path}")
    
    # Показываем график
    plt.show()

def main():
    """Основная функция анализа."""
    print("Анализ завершения курсов")
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
        print(f"Начали: {row['students_started']}, Завершили: {row['students_completed']}")
        completion_rate = row['students_completed'] / row['students_started'] if row['students_started'] > 0 else 0
        print(f"Доля завершивших: {completion_rate:.1%}")
        print("-" * 30)
    
    # Строим диаграмму
    plot_course_completion(df)

if __name__ == "__main__":
    main()