from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from .models import Course, CourseFinalKnowledge, CourseRequiredKnowledge, StudentKnowledge, Knowledge, Tag, CourseCard, Card, StudentCard, CardKnowledge
from datetime import datetime
from . import db

courses = Blueprint('courses', __name__)

@courses.route('/courses')
@login_required
def course_list():
    # Get tag filter if provided
    tag_filter = request.args.get('tag')
    
    # Get all available tags for filtering
    all_tags = Tag.query.all()
    
    # Get all knowledges for display
    all_knowledges = Knowledge.query.all()
    
    # Initialize user_knowledges
    user_knowledges = {}

    # Get all available courses, filtered by tag if specified
    if tag_filter:
        # Find courses with the selected tag
        tag = Tag.query.filter_by(name=tag_filter).first()
        if tag:
            all_courses = [tc.course for tc in tag.courses]
        else:
            all_courses = Course.query.all()
    else:
        all_courses = Course.query.all()
    
    # Update user knowledge based on marked cards
    for sk in current_user.knowledges:
        # Get the knowledge associated with this student
        knowledge = Knowledge.query.get(sk.knowledge_id)
        if knowledge:
            # Get all cards associated with this knowledge
            associated_cards = Card.query.join(Card.knowledges).filter(CardKnowledge.knowledge_id == knowledge.id).all()
            total_quality_gain = 0
            for card in associated_cards:
                # Check if the student has marked this card
                student_card = StudentCard.query.filter_by(student_id=current_user.id, card_id=card.id).first()
                if student_card:
                    # Get the quality of the card for the specific knowledge
                    card_knowledge = CardKnowledge.query.filter_by(card_id=card.id, knowledge_id=knowledge.id).first()
                    if card_knowledge:
                        # Calculate knowledge gain based on the mark and quality
                        total_quality_gain += student_card.mark * card_knowledge.quality
            # Update the student's knowledge quality
            sk.quality = min(100, sk.quality + total_quality_gain)
            sk.last_update = datetime.utcnow()
    
    # Calculate progress for each course
    course_data = []
    for course in all_courses:
        # Get required knowledges for the course
        required_knowledges = CourseRequiredKnowledge.query.filter_by(course_id=course.id).all()
        
        # Get final knowledges provided by the course
        final_knowledges = CourseFinalKnowledge.query.filter_by(course_id=course.id).all()
        
        # Calculate if user has prerequisites
        # Create a lookup dictionary with both integer IDs and string names
        user_knowledges = {}
        for sk in current_user.knowledges:
            # Store by ID
            user_knowledges[sk.knowledge_id] = sk.quality
            # Also store by name if we can find the knowledge
            k_obj = Knowledge.query.get(sk.knowledge_id)
            if k_obj:
                user_knowledges[k_obj.name] = sk.quality
        
        missing_prerequisites = []
        for req in required_knowledges:
            # Convert text knowledge_id to int if necessary (depends on your data model)
            try:
                k_id = int(req.knowledge_id)
            except ValueError:
                k_id = req.knowledge_id
                
            if k_id not in user_knowledges or user_knowledges[k_id] < req.quality:
                # Find the knowledge name
                # Get knowledge by name if it's a string, otherwise by ID
                if isinstance(k_id, str):
                    k_obj = Knowledge.query.filter_by(name=k_id).first()
                else:
                    k_obj = Knowledge.query.filter_by(id=k_id).first()
                knowledge_name = k_obj.name if k_obj else f"Knowledge #{k_id}"
                missing_prerequisites.append({
                    'name': knowledge_name,
                    'required': req.quality,
                    'current': user_knowledges.get(k_id, 0)
                })
        
        # Use course time from database
        estimated_time = course.estimated_time
        
        # Add to course data - always set can_start to True
        course_data.append({
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'estimated_time': estimated_time,
            'missing_prerequisites': missing_prerequisites,
            'can_start': True  # Allow starting any course regardless of prerequisites
        })
    
    # Get all user's knowledge including those with zero quality
    all_user_knowledge = []
    for k in all_knowledges:
        quality = user_knowledges.get(k.id, 0)
        all_user_knowledge.append({
            'id': k.id,
            'name': k.name,
            'description': k.description,
            'quality': quality
        })
    
    # Sort by quality (descending)
    all_user_knowledge.sort(key=lambda x: x['quality'], reverse=True)
    
    return render_template('courses.html', 
                           courses=course_data, 
                           tags=all_tags, 
                           selected_tag=tag_filter,
                           knowledges=all_user_knowledge)

@courses.route('/courses/<int:course_id>/start')
@login_required
def start_course(course_id):
    # Check if user has prerequisites
    course = Course.query.get_or_404(course_id)
    required_knowledges = CourseRequiredKnowledge.query.filter_by(course_id=course.id).all()
    
    # Create a lookup dictionary with both integer IDs and string names
    user_knowledges_by_id = {}
    
    for sk in current_user.knowledges:
        # Store by ID
        user_knowledges_by_id[sk.knowledge_id] = sk.quality
        # Also store by name if we can find the knowledge
        knowledge = Knowledge.query.get(sk.knowledge_id)
        if knowledge:
            user_knowledges_by_id[knowledge.name] = sk.quality
    
    missing_prerequisites = []
    for req in required_knowledges:
        try:
            k_id = int(req.knowledge_id)
        except ValueError:
            k_id = req.knowledge_id
        if k_id not in user_knowledges_by_id or user_knowledges_by_id[k_id] < req.quality:
            missing_prerequisites.append(req)
    
    # Always allow users to start the course, just display a warning if prerequisites are missing
    if missing_prerequisites:
        from flask import flash
        flash('Warning: You do not have all the prerequisites for this course, but you can still proceed.')
    # Get all cards associated with this course
    course_cards_associations = CourseCard.query.filter_by(course_id=course.id).all()
    course_cards = []
    
    for assoc in course_cards_associations:
        card = Card.query.get(assoc.card_id)
        if card:
            # Check if student has completed this card
            student_card = StudentCard.query.filter_by(
                student_id=current_user.id,
                card_id=card.id
            ).first()
            
            completed = student_card is not None and student_card.mark is not None
            
            course_cards.append({
                'id': card.id,
                'question': card.question,
                'answer': card.answer,
                'completed': completed
            })
    
    # Get knowledge outcomes for this course
    final_knowledge_associations = CourseFinalKnowledge.query.filter_by(course_id=course.id).all()
    final_knowledges = []
    
    for assoc in final_knowledge_associations:
        # Try to find knowledge by ID or name
        try:
            k_id = int(assoc.knowledge_id)
            knowledge = Knowledge.query.get(k_id)
        except ValueError:
            knowledge = Knowledge.query.filter_by(name=assoc.knowledge_id).first()
        
        if knowledge:
            final_knowledges.append({
                'id': knowledge.id,
                'name': knowledge.name, 
                'description': knowledge.description,
                'quality': assoc.quality
            })
        else:
            # If we can't find the knowledge, still show the ID/name
            final_knowledges.append({
                'id': None,
                'name': assoc.knowledge_id,
                'description': None,
                'quality': assoc.quality
            })
    
    return render_template('course_view.html', 
                          course=course, 
                          course_cards=course_cards, 
                          final_knowledges=final_knowledges)

@courses.route('/cards/<int:card_id>/mark', methods=['POST'])
@login_required
def mark_card(card_id):
    """Mark a card as completed with a difficulty rating."""
    # Get the card
    card = Card.query.get_or_404(card_id)
    
    # Get difficulty from request data
    data = request.get_json()
    difficulty = data.get('difficulty', 'normal')
    
    # Convert difficulty to numerical score (0-10)
    mark = {
        'hard': 3,   # Struggled with the card
        'normal': 6,  # Average understanding
        'easy': 9     # Easily understood
    }.get(difficulty, 6)  # Default to 'normal' if invalid difficulty
    
    # Check if student has already marked this card
    student_card = StudentCard.query.filter_by(
        student_id=current_user.id,
        card_id=card.id
    ).first()
    
    if student_card:
        # Update existing record
        student_card.mark = mark
        student_card.time = datetime.utcnow()
    else:
        # Create new record
        student_card = StudentCard(
            student_id=current_user.id,
            card_id=card.id,
            mark=mark,
            time=datetime.utcnow()
        )
        db.session.add(student_card)
    
    # Also update student knowledge for all knowledge areas this card covers
    for card_knowledge in card.knowledges:
        knowledge_id = card_knowledge.knowledge_id
        knowledge_quality = card_knowledge.quality
        
        # Calculate how much this improves student's knowledge
        # Formula: Card knowledge quality * (card_mark / 10) = knowledge gained
        knowledge_gain = int(knowledge_quality * (mark / 10))
        
        # Find if student already has this knowledge
        student_knowledge = StudentKnowledge.query.filter_by(
            student_id=current_user.id,
            knowledge_id=knowledge_id
        ).first()
        
        if student_knowledge:
            # Update existing knowledge - simple average for now
            # Could be made more sophisticated with recency bias, etc.
            student_knowledge.quality = min(100, student_knowledge.quality + knowledge_gain)
            student_knowledge.last_update = datetime.utcnow()
        else:
            # Create new knowledge entry
            student_knowledge = StudentKnowledge(
                student_id=current_user.id,
                knowledge_id=knowledge_id,
                quality=knowledge_gain,
                last_update=datetime.utcnow()
            )
            db.session.add(student_knowledge)
    
    # Commit all changes
    db.session.commit()
    
    return jsonify({'success': True, 'mark': mark})
