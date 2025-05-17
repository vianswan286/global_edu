from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from .models import Knowledge, StudentKnowledge, Course, CourseCard, Card, StudentCard, CourseFinalKnowledge, CourseRequiredKnowledge
from collections import defaultdict

knowledge_shop = Blueprint('knowledge_shop', __name__)

@knowledge_shop.route('/knowledge-shop')
@login_required
def shop_view():
    """Перенаправление на новый интерфейс выбора знаний"""
    return redirect(url_for('knowledge_shop.simple_knowledge_courses'))
    
@knowledge_shop.route('/simple-knowledge-courses', methods=['GET'])
@login_required
def simple_knowledge_courses():
    """Простая страница для выбора знаний и отображения курсов"""
    # Получаем все знания
    all_knowledge = Knowledge.query.all()
    
    # Получаем текущий уровень знаний студента
    student_knowledge = {}
    for sk in StudentKnowledge.query.filter_by(student_id=current_user.id).all():
        student_knowledge[sk.knowledge_id] = sk.quality
    
    # Подготавливаем данные для шаблона
    knowledge_data = []
    for k in all_knowledge:
        knowledge_data.append({
            'id': k.id,
            'name': k.name,
            'description': k.description,
            'current_quality': student_knowledge.get(k.id, 0)
        })
    
    # Сортируем знания по имени
    knowledge_data.sort(key=lambda x: x['name'])
    
    # Получаем все курсы и их знания
    all_courses = Course.query.all()
    
    # Для каждого курса получаем знания, которые он дает
    courses_data = []
    for course in all_courses:
        # Получаем знания, которые дает курс
        provided_knowledges = []
        for cfk in CourseFinalKnowledge.query.filter_by(course_id=course.id).all():
            # Пробуем разные способы получения знания
            knowledge = None
            
            # Способ 1: Пробуем преобразовать knowledge_id в целое число
            try:
                knowledge_id = int(cfk.knowledge_id)
                knowledge = Knowledge.query.get(knowledge_id)
            except (ValueError, TypeError):
                pass
                
            # Способ 2: Пробуем найти знание по имени
            if knowledge is None:
                knowledge = Knowledge.query.filter_by(name=cfk.knowledge_id).first()
            
            if knowledge:
                provided_knowledges.append({
                    'id': knowledge.id,
                    'name': knowledge.name
                })
        
        courses_data.append({
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'provided_knowledges': provided_knowledges
        })
    
    return render_template('simple_knowledge_courses.html', 
                          knowledges=knowledge_data,
                          recommended_courses=courses_data,
                          selected_knowledges=None,
                          selected_knowledge_ids=[])
                          
@knowledge_shop.route('/show-courses-for-knowledge', methods=['POST'])
@login_required
def show_courses_for_knowledge():
    """Показать 2 случайных курса для выбранных знаний"""
    import random
    
    # Получаем выбранные знания из формы
    knowledge_ids = request.form.getlist('knowledge_ids')
    
    # Преобразуем строковые ID в целые числа
    knowledge_ids = [int(kid) for kid in knowledge_ids if kid.isdigit()]
    
    if not knowledge_ids:
        flash('Выберите хотя бы одно знание', 'warning')
        return redirect(url_for('knowledge_shop.simple_knowledge_courses'))
    
    # Получаем все знания
    all_knowledge = Knowledge.query.all()
    
    # Подготавливаем данные для шаблона
    knowledge_data = []
    for k in all_knowledge:
        knowledge_data.append({
            'id': k.id,
            'name': k.name,
            'description': k.description
        })
    
    # Сортируем знания по имени
    knowledge_data.sort(key=lambda x: x['name'])
    
    # Получаем выбранные знания
    selected_knowledges = [k for k in knowledge_data if k['id'] in knowledge_ids]
    
    # Получаем все курсы
    all_courses = Course.query.all()
    
    # Для каждого курса получаем знания, которые он дает
    courses_data = []
    for course in all_courses:
        # Получаем знания, которые дает курс
        provided_knowledges = []
        for cfk in CourseFinalKnowledge.query.filter_by(course_id=course.id).all():
            # Пробуем разные способы получения знания
            knowledge = None
            
            # Способ 1: Пробуем преобразовать knowledge_id в целое число
            try:
                knowledge_id = int(cfk.knowledge_id)
                knowledge = Knowledge.query.get(knowledge_id)
            except (ValueError, TypeError):
                pass
                
            # Способ 2: Пробуем найти знание по имени
            if knowledge is None:
                knowledge = Knowledge.query.filter_by(name=cfk.knowledge_id).first()
            
            if knowledge:
                provided_knowledges.append({
                    'id': knowledge.id,
                    'name': knowledge.name
                })
        
        courses_data.append({
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'provided_knowledges': provided_knowledges
        })
    
    # Выбираем 2 случайных курса
    if len(courses_data) > 2:
        recommended_courses = random.sample(courses_data, 2)
    else:
        recommended_courses = courses_data
    
    return render_template('simple_knowledge_courses.html', 
                          knowledges=knowledge_data,
                          recommended_courses=recommended_courses,
                          selected_knowledges=selected_knowledges,
                          selected_knowledge_ids=knowledge_ids)

@knowledge_shop.route('/knowledge-selector')
@login_required
def knowledge_selector():
    """Страница выбора знаний для изучения"""
    # Получаем все знания
    all_knowledge = Knowledge.query.all()
    
    # Получаем текущий уровень знаний студента
    student_knowledge = {}
    for sk in StudentKnowledge.query.filter_by(student_id=current_user.id).all():
        student_knowledge[sk.knowledge_id] = sk.quality
    
    # Подготавливаем данные для шаблона
    knowledge_data = []
    for k in all_knowledge:
        # Получаем курсы, которые дают это знание
        providing_courses = []
        for cfk in CourseFinalKnowledge.query.filter_by(knowledge_id=str(k.id)).all():
            course = Course.query.get(cfk.course_id)
            if course:
                providing_courses.append({
                    'id': course.id,
                    'name': course.name,
                    'quality': cfk.quality
                })
        
        knowledge_data.append({
            'id': k.id,
            'name': k.name,
            'description': k.description,
            'theory': k.theory,
            'current_quality': student_knowledge.get(k.id, 0),
            'providing_courses': providing_courses
        })
    
    # Сортируем знания по имени
    knowledge_data.sort(key=lambda x: x['name'])
    
    # Получаем выбранные знания из сессии
    knowledge_cart = session.get('knowledge_cart', [])
    
    return render_template('knowledge_selector.html', 
                          knowledges=knowledge_data,
                          cart=knowledge_cart)

@knowledge_shop.route('/knowledge-shop/add-knowledge', methods=['POST'])
@login_required
def add_knowledge_to_cart():
    """Добавление знания в список выбранных"""
    # Проверяем, что данные пришли в формате JSON
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Ожидается JSON'}), 400
        
    data = request.get_json()
    knowledge_id = data.get('knowledge_id')
    
    # Преобразуем knowledge_id в int, так как из JSON он может прийти как строка
    try:
        knowledge_id = int(knowledge_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Некорректный ID знания'}), 400
    
    if not knowledge_id:
        return jsonify({'success': False, 'message': 'Не указан ID знания'}), 400
    
    # Проверяем, существует ли знание
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return jsonify({'success': False, 'message': 'Знание не найдено'}), 404
    
    # Получаем список из сессии
    knowledge_cart = session.get('knowledge_cart', [])
    
    # Преобразуем все ID в списке в int для корректного сравнения
    knowledge_cart = [int(k_id) for k_id in knowledge_cart]
    
    # Добавляем знание, если его еще нет в списке
    if knowledge_id not in knowledge_cart:
        knowledge_cart.append(knowledge_id)
        session['knowledge_cart'] = knowledge_cart
        # Принудительно сохраняем сессию
        session.modified = True
        
        return jsonify({
            'success': True, 
            'message': f'Знание "{knowledge.name}" добавлено в список',
            'cart_count': len(knowledge_cart)
        })
    else:
        return jsonify({'success': False, 'message': 'Это знание уже в списке'})

@knowledge_shop.route('/knowledge-shop/remove-knowledge', methods=['POST'])
@login_required
def remove_knowledge_from_cart():
    """Удаление знания из списка выбранных"""
    # Проверяем, что данные пришли в формате JSON
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Ожидается JSON'}), 400
        
    data = request.get_json()
    knowledge_id = data.get('knowledge_id')
    
    # Преобразуем knowledge_id в int, так как из JSON он может прийти как строка
    try:
        knowledge_id = int(knowledge_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Некорректный ID знания'}), 400
    
    if not knowledge_id:
        return jsonify({'success': False, 'message': 'Не указан ID знания'}), 400
    
    # Получаем список из сессии
    knowledge_cart = session.get('knowledge_cart', [])
    
    # Преобразуем все ID в списке в int для корректного сравнения
    knowledge_cart = [int(k_id) for k_id in knowledge_cart]
    
    # Удаляем знание, если оно есть в списке
    if knowledge_id in knowledge_cart:
        knowledge_cart.remove(knowledge_id)
        session['knowledge_cart'] = knowledge_cart
        # Принудительно сохраняем сессию
        session.modified = True
        
        # Получаем название знания для сообщения
        knowledge = Knowledge.query.get(knowledge_id)
        knowledge_name = knowledge.name if knowledge else 'Знание'
        
        return jsonify({
            'success': True, 
            'message': f'Знание "{knowledge_name}" удалено из списка',
            'cart_count': len(knowledge_cart)
        })
    else:
        return jsonify({'success': False, 'message': 'Этого знания нет в списке'})

@knowledge_shop.route('/knowledge-shop/recommend-courses')
@login_required
def recommend_courses():
    """Страница с рекомендуемыми курсами на основе выбранных знаний"""
    # Получаем выбранные знания из сессии
    knowledge_ids = session.get('knowledge_cart', [])
    
    if not knowledge_ids:
        return render_template('recommended_courses.html', 
                              target_knowledges=[],
                              target_knowledge_ids=[],
                              recommended_courses=[])
    
    # Получаем детали выбранных знаний
    target_knowledges = []
    for knowledge_id in knowledge_ids:
        knowledge = Knowledge.query.get(knowledge_id)
        if knowledge:
            # Получаем текущий уровень знания студента
            student_knowledge = StudentKnowledge.query.filter_by(
                student_id=current_user.id,
                knowledge_id=knowledge_id
            ).first()
            
            current_quality = student_knowledge.quality if student_knowledge else 0
            
            target_knowledges.append({
                'id': knowledge_id,
                'name': knowledge.name,
                'description': knowledge.description,
                'current_quality': current_quality
            })
    
    # Находим курсы, которые помогут получить выбранные знания
    recommended_courses = find_courses_for_knowledges(knowledge_ids)
    
    return render_template('recommended_courses.html', 
                          target_knowledges=target_knowledges,
                          target_knowledge_ids=knowledge_ids,
                          recommended_courses=recommended_courses)

@knowledge_shop.route('/knowledge-shop/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    """Очистка списка выбранных знаний"""
    session['knowledge_cart'] = []
    # Принудительно сохраняем сессию
    session.modified = True
    
    return jsonify({
        'success': True, 
        'message': 'Список выбранных знаний очищен',
        'cart_count': 0
    })

def find_courses_for_knowledges(target_knowledge_ids):
    """Находит курсы, которые помогут получить выбранные знания.
    
    Args:
        target_knowledge_ids: Список ID знаний, которые студент хочет получить
    
    Returns:
        Список рекомендуемых курсов, отсортированный по релевантности
    """
    if not target_knowledge_ids:
        return []
    
    # Получаем текущий уровень знаний студента
    current_knowledge = {}
    for sk in StudentKnowledge.query.filter_by(student_id=current_user.id).all():
        current_knowledge[sk.knowledge_id] = sk.quality
    
    # Получаем все курсы
    all_courses = Course.query.all()
    course_data = {}
    
    # Для каждого курса определяем, какие знания он дает и насколько релевантен
    for course in all_courses:
        # Получаем все знания, которые дает этот курс
        provided_knowledges = []
        for cfk in CourseFinalKnowledge.query.filter_by(course_id=course.id).all():
            try:
                knowledge_id = int(cfk.knowledge_id)
                knowledge = Knowledge.query.get(knowledge_id)
                if knowledge:
                    provided_knowledges.append({
                        'id': knowledge_id,
                        'name': knowledge.name,
                        'quality': cfk.quality
                    })
            except (ValueError, TypeError):
                # Обрабатываем случай, когда knowledge_id не является целым числом
                pass
        
        # Получаем прогресс по курсу
        course_cards = [cc.card_id for cc in CourseCard.query.filter_by(course_id=course.id).all()]
        total_cards = len(course_cards)
        
        if total_cards > 0:
            completed_cards = StudentCard.query.filter(
                StudentCard.student_id == current_user.id,
                StudentCard.card_id.in_(course_cards),
                StudentCard.mark.isnot(None)
            ).count()
            progress_percent = (completed_cards / total_cards) * 100
        else:
            completed_cards = 0
            progress_percent = 0
        
        # Получаем необходимые знания для курса
        prerequisites = []
        missing_prerequisites = []
        
        for prereq in CourseRequiredKnowledge.query.filter_by(course_id=course.id).all():
            try:
                prereq_id = int(prereq.knowledge_id)
                knowledge = Knowledge.query.get(prereq_id)
                if knowledge:
                    # Проверяем уровень знания студента
                    student_level = current_knowledge.get(prereq_id, 0)
                    required_level = prereq.quality
                    
                    prereq_data = {
                        'knowledge': knowledge,
                        'required_quality': required_level,
                        'current_quality': student_level,
                        'is_met': student_level >= required_level,
                        'quality_gap': max(0, required_level - student_level)
                    }
                    
                    prerequisites.append(prereq_data)
                    
                    # Если необходимое знание отсутствует, добавляем в список отсутствующих
                    if not prereq_data['is_met']:
                        missing_prerequisites.append(prereq_data)
            except (ValueError, TypeError):
                # Обрабатываем случай, когда knowledge_id не является целым числом
                pass
        
        # Вычисляем процент выполненных необходимых знаний
        if prerequisites:
            prereq_met_count = sum(1 for p in prerequisites if p['is_met'])
            prereq_met_percent = (prereq_met_count / len(prerequisites)) * 100
        else:
            prereq_met_percent = 100  # Если нет необходимых знаний, считаем 100%
        
        # Вычисляем релевантность курса для выбранных знаний
        relevant_knowledge_count = sum(1 for k in provided_knowledges if k['id'] in target_knowledge_ids)
        if provided_knowledges:
            relevance_score = (relevant_knowledge_count / len(provided_knowledges)) * 100
            # Если курс дает хотя бы одно из выбранных знаний, даем ему минимальный балл 30
            if relevant_knowledge_count > 0 and relevance_score < 30:
                relevance_score = 30
        else:
            relevance_score = 0
        
        # Сохраняем данные о курсе
        course_data[course.id] = {
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'estimated_time': course.estimated_time,
            'completed_cards': completed_cards,
            'total_cards': total_cards,
            'progress_percent': progress_percent,
            'provided_knowledges': provided_knowledges,
            'prerequisites': prerequisites,
            'missing_prerequisites': missing_prerequisites,
            'prereq_met_percent': prereq_met_percent,
            'relevance_score': relevance_score
        }
    
    # Отбираем только курсы с ненулевой релевантностью
    relevant_courses = [course for course_id, course in course_data.items() if course['relevance_score'] > 0]
    
    # Сортируем курсы по релевантности (от высокой к низкой)
    relevant_courses.sort(key=lambda x: (-x['relevance_score'], -x['prereq_met_percent']))
    
    return relevant_courses
