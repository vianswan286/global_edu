from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import StudentKnowledge, Knowledge

knowledge = Blueprint('knowledge', __name__)

@knowledge.route('/knowledge')
@login_required
def knowledge_list():
    # Get all user's knowledge
    user_knowledges = StudentKnowledge.query.filter_by(student_id=current_user.id).all()
    
    # Create a list of knowledge with details
    knowledge_data = []
    for sk in user_knowledges:
        k = Knowledge.query.get(sk.knowledge_id)
        if k:
            knowledge_data.append({
                'id': k.id,
                'name': k.name,
                'description': k.description,
                'quality': sk.quality,
                'last_update': sk.last_update
            })
    
    # Sort by quality (descending)
    knowledge_data.sort(key=lambda x: x['quality'], reverse=True)
    
    return render_template('knowledge.html', knowledges=knowledge_data)

@knowledge.route('/knowledge/<knowledge_id>')
@login_required
def knowledge_detail(knowledge_id):
    # Get the knowledge by ID or name
    try:
        # Try to convert to integer ID
        id_value = int(knowledge_id)
        k = Knowledge.query.get_or_404(id_value)
    except ValueError:
        # If not an integer, search by name
        k = Knowledge.query.filter_by(name=knowledge_id).first_or_404()
    
    # Get user's quality for this knowledge
    # We need to use the ID from the knowledge object we found
    knowledge_id_to_use = k.id
    sk = StudentKnowledge.query.filter_by(student_id=current_user.id, knowledge_id=knowledge_id_to_use).first()
    
    quality = sk.quality if sk else 0
    
    # Get courses that provide this knowledge
    from .models import Course, CourseFinalKnowledge, CourseCard, StudentCard
    from sqlalchemy import func
    
    # Find courses related to this knowledge
    related_courses = []
    course_connections = CourseFinalKnowledge.query.filter_by(knowledge_id=str(knowledge_id_to_use)).all()
    
    for connection in course_connections:
        course = Course.query.get(connection.course_id)
        if course:
            # Calculate student progress in this course
            course_cards = CourseCard.query.filter_by(course_id=course.id).count()
            completed_cards = 0
            if course_cards > 0:
                completed_cards = StudentCard.query.filter(
                    StudentCard.student_id == current_user.id,
                    StudentCard.card_id.in_([cc.card_id for cc in CourseCard.query.filter_by(course_id=course.id)])  
                ).filter(StudentCard.mark.isnot(None)).count()
            
            progress_percent = (completed_cards / course_cards * 100) if course_cards > 0 else 0
            
            related_courses.append({
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'quality': connection.quality,  # Knowledge quality this course provides
                'estimated_time': course.estimated_time,
                'progress_percent': progress_percent,
                'completed_cards': completed_cards,
                'total_cards': course_cards
            })
    
    # Sort courses by how much knowledge quality they provide (most first)
    related_courses.sort(key=lambda x: x['quality'], reverse=True)
    
    return render_template('knowledge_detail.html', knowledge=k, quality=quality, related_courses=related_courses)
