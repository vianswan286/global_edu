from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from .models import Knowledge, StudentKnowledge, Course, CourseCard, Card, StudentCard, CourseFinalKnowledge, CourseRequiredKnowledge
from collections import defaultdict

knowledge_shop = Blueprint('knowledge_shop', __name__)

@knowledge_shop.route('/knowledge-shop')
@login_required
def shop_view():
    """
    Main view for the Knowledge Shop feature.
    Shows all available knowledge units and lets students select ones they want to learn.
    """
    # Get all knowledge units
    all_knowledge = Knowledge.query.all()
    
    # Get student's existing knowledge quality
    student_knowledge = {}
    for sk in StudentKnowledge.query.filter_by(student_id=current_user.id).all():
        student_knowledge[sk.knowledge_id] = sk.quality
    
    # Prepare data for the template
    knowledge_data = []
    for k in all_knowledge:
        # Get courses that provide this knowledge
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
    
    # Sort knowledge by name
    knowledge_data.sort(key=lambda x: x['name'])
    
    # Get the knowledge cart from session
    knowledge_cart = session.get('knowledge_cart', [])
    
    return render_template('knowledge_shop.html', 
                          knowledges=knowledge_data,
                          cart=knowledge_cart)

@knowledge_shop.route('/knowledge-shop/add-knowledge', methods=['POST'])
@login_required
def add_knowledge_to_cart():
    """
    Add a knowledge unit to the shopping cart.
    """
    knowledge_id = request.json.get('knowledge_id')
    
    if not knowledge_id:
        return jsonify({'success': False, 'message': 'No knowledge ID provided'})
    
    # Make sure knowledge exists
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return jsonify({'success': False, 'message': 'Knowledge not found'})
    
    # Get cart from session
    knowledge_cart = session.get('knowledge_cart', [])
    
    # Add knowledge to cart if not already in
    if knowledge_id not in knowledge_cart:
        knowledge_cart.append(knowledge_id)
        session['knowledge_cart'] = knowledge_cart
        return jsonify({'success': True, 'message': f'Added {knowledge.name} to your learning goals'})
    else:
        return jsonify({'success': False, 'message': 'Knowledge already in learning goals'})

@knowledge_shop.route('/knowledge-shop/remove-knowledge', methods=['POST'])
@login_required
def remove_knowledge_from_cart():
    """
    Remove a knowledge unit from the shopping cart.
    """
    knowledge_id = request.json.get('knowledge_id')
    
    if not knowledge_id:
        return jsonify({'success': False, 'message': 'No knowledge ID provided'})
    
    # Get cart from session
    knowledge_cart = session.get('knowledge_cart', [])
    
    # Remove knowledge from cart if it's there
    if knowledge_id in knowledge_cart:
        knowledge_cart.remove(knowledge_id)
        session['knowledge_cart'] = knowledge_cart
        
        # Get knowledge name for more helpful message
        knowledge = Knowledge.query.get(knowledge_id)
        knowledge_name = knowledge.name if knowledge else 'Knowledge'
        
        return jsonify({'success': True, 'message': f'Removed {knowledge_name} from learning goals'})
    else:
        return jsonify({'success': False, 'message': 'Knowledge not in learning goals'})

@knowledge_shop.route('/knowledge-shop/view-roadmap')
@login_required
def view_roadmap():
    """
    View the learning roadmap for selected target knowledge units.
    Recommends courses to take based on prerequisites and desired knowledge.
    """
    # Get the knowledge cart from session
    knowledge_ids = session.get('knowledge_cart', [])
    
    if not knowledge_ids:
        return render_template('course_roadmap.html', 
                              target_knowledges=[],
                              recommended_courses=[],
                              missing_prerequisites=[])
    
    # Get knowledge details for cart items
    target_knowledges = []
    for knowledge_id in knowledge_ids:
        knowledge = Knowledge.query.get(knowledge_id)
        if knowledge:
            # Get student's current knowledge quality
            student_knowledge = StudentKnowledge.query.filter_by(
                student_id=current_user.id,
                knowledge_id=knowledge_id
            ).first()
            
            current_quality = student_knowledge.quality if student_knowledge else 0
            quality_gap = max(0, 100 - current_quality)  # Assuming max quality is 100
            
            target_knowledges.append({
                'knowledge': knowledge,
                'current_quality': current_quality,
                'quality_gap': quality_gap,
                'progress_percent': current_quality  # Since max is 100
            })
    
    # Create course roadmap to achieve target knowledge
    roadmap_data = create_course_roadmap(knowledge_ids)
    
    return render_template('course_roadmap.html', 
                          target_knowledges=target_knowledges,
                          recommended_courses=roadmap_data['recommended_courses'],
                          prerequisites=roadmap_data['prerequisites'],
                          missing_prerequisites=roadmap_data['missing_prerequisites'],
                          allow_skip_percent=roadmap_data['allow_skip_percent'])

@knowledge_shop.route('/knowledge-shop/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    """
    Clear the entire knowledge cart.
    """
    session['knowledge_cart'] = []
    
    return jsonify({
        'success': True, 
        'message': 'Learning goals cleared',
        'cart_count': 0
    })

def create_course_roadmap(target_knowledge_ids):
    """
    Create a learning roadmap that shows which courses to take to acquire
    the target knowledge, considering prerequisites.
    
    Args:
        target_knowledge_ids: List of knowledge IDs the student wants to learn
    
    Returns:
        Dictionary with recommended courses, prerequisites, and skip percentage
    """
    if not target_knowledge_ids:
        return {
            'recommended_courses': [], 
            'prerequisites': [], 
            'missing_prerequisites': [], 
            'allow_skip_percent': 0
        }
    
    # Build knowledge and course graphs
    knowledge_prerequisites = defaultdict(list)  # Knowledge -> prerequisite knowledge
    courses_by_final_knowledge = defaultdict(list)  # Knowledge -> courses that teach it
    courses_by_required_knowledge = defaultdict(list)  # Knowledge -> courses that need it
    course_details = {}
    
    # Get all courses
    all_courses = Course.query.all()
    
    # Get student's current knowledge
    # Get student's current knowledge
    current_knowledge = {}
    for sk in StudentKnowledge.query.filter_by(student_id=current_user.id).all():
        current_knowledge[sk.knowledge_id] = sk.quality
    
    # Find courses that teach the target knowledge
    recommended_courses_set = set()  # Use a set to avoid duplicates
    
    # For each target knowledge, find courses that teach it
    for knowledge_id in target_knowledge_ids:
        knowledge = Knowledge.query.get(knowledge_id)
        if not knowledge:
            continue
            
        # Find courses that provide this knowledge
        for cfk in CourseFinalKnowledge.query.filter_by(knowledge_id=str(knowledge_id)).all():
            course = Course.query.get(cfk.course_id)
            if course:
                courses_by_final_knowledge[knowledge_id].append({
                    'course_id': course.id,
                    'course': course,
                    'quality': cfk.quality
                })
                recommended_courses_set.add(course.id)
    
    # Get details for all relevant courses and check their prerequisites
    course_details = {}
    all_prerequisites = []
    missing_prerequisites = []
    
    # Get details for each course that teaches our target knowledge
    for course_id in recommended_courses_set:
        course = Course.query.get(course_id)
        if not course:
            continue
            
        # Get progress information for this course
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
            
        # Initialize course details
        course_details[course_id] = {
            'course': course,
            'completed_cards': completed_cards,
            'total_cards': total_cards,
            'progress_percent': progress_percent,
            'prerequisites': [],
            'missing_prerequisites': [],
            'provides_target_knowledge': False
        }
        
        # Mark if this course provides any of our target knowledge
        for k_id in target_knowledge_ids:
            if any(cfk.knowledge_id == str(k_id) for cfk in CourseFinalKnowledge.query.filter_by(course_id=course.id).all()):
                course_details[course_id]['provides_target_knowledge'] = True
                break
                
        # Get prerequisites for this course
        for prereq in CourseRequiredKnowledge.query.filter_by(course_id=course.id).all():
            try:
                prereq_id = int(prereq.knowledge_id)
                knowledge = Knowledge.query.get(prereq_id)
                if knowledge:
                    # Check student's knowledge level
                    student_level = current_knowledge.get(prereq_id, 0)
                    required_level = prereq.quality
                    
                    prereq_data = {
                        'knowledge': knowledge,
                        'required_quality': required_level,
                        'current_quality': student_level,
                        'is_met': student_level >= required_level,
                        'quality_gap': max(0, required_level - student_level)
                    }
                    
                    all_prerequisites.append(prereq_data)
                    course_details[course_id]['prerequisites'].append(prereq_data)
                    
                    # If prerequisite not met, add to missing
                    if not prereq_data['is_met']:
                        course_details[course_id]['missing_prerequisites'].append(prereq_data)
                        missing_prerequisites.append(prereq_data)
            except (ValueError, TypeError):
                # Handle case where knowledge_id is not a valid integer
                pass
    
    # Create a dependency graph to compute course levels
    # First, find courses that have no missing prerequisites - these are level 0
    level_0_courses = []
    for course_id, details in course_details.items():
        if not details['missing_prerequisites']:
            level_0_courses.append(course_id)
            
    # Create an adjacency list for course prerequisites
    course_dependencies = defaultdict(list)
    for course_id, details in course_details.items():
        # For each missing knowledge, find courses that provide it
        for prereq in details['missing_prerequisites']:
            knowledge_id = prereq['knowledge'].id
            for course_info in courses_by_final_knowledge.get(knowledge_id, []):
                if course_info['course_id'] != course_id:  # Don't create self-loops
                    course_dependencies[course_id].append(course_info['course_id'])
    
    # Assign levels based on dependency depth
    course_levels = {}
    visited = set()
    
    # Start with level 0 courses (no missing prerequisites)
    for course_id in level_0_courses:
        course_levels[course_id] = 0
        visited.add(course_id)
        
    # For remaining courses, assign levels based on dependencies
    # The more dependencies, the higher the level
    remaining_courses = [c_id for c_id in course_details.keys() if c_id not in level_0_courses]
    
    # Sort by number of missing prerequisites
    remaining_courses.sort(key=lambda x: len(course_details[x]['missing_prerequisites']))
    
    for course_id in remaining_courses:
        if course_id not in visited:
            # Level = 1 + maximum dependency level
            dependency_levels = [course_levels.get(dep, 0) for dep in course_dependencies[course_id]]
            level = 1 + (max(dependency_levels) if dependency_levels else 0)
            course_levels[course_id] = level
            visited.add(course_id)
    
    # Prepare the final course list ordered by level
    recommended_courses = []
    
    # Add primary courses (those that directly teach target knowledge) first, ordered by level
    primary_courses = [(course_id, details) for course_id, details in course_details.items() 
                      if details['provides_target_knowledge']]
    primary_courses.sort(key=lambda x: (course_levels.get(x[0], 0), len(x[1]['missing_prerequisites'])))
    
    for course_id, details in primary_courses:
        details['level'] = course_levels.get(course_id, 0)
        details['is_primary'] = True
        recommended_courses.append(details)
    
    # Add prerequisite courses that don't directly teach target knowledge
    secondary_courses = [(course_id, details) for course_id, details in course_details.items() 
                       if not details['provides_target_knowledge']]
    secondary_courses.sort(key=lambda x: (course_levels.get(x[0], 0), len(x[1]['missing_prerequisites'])))
    
    for course_id, details in secondary_courses:
        details['level'] = course_levels.get(course_id, 0)
        details['is_primary'] = False
        recommended_courses.append(details)
    
    # Calculate how many prerequisites need to be skipped
    total_prereqs = sum(len(course['prerequisites']) for course in recommended_courses if course['prerequisites'])
    missing_prereqs = sum(len(course['missing_prerequisites']) for course in recommended_courses if course['missing_prerequisites'])
    
    if total_prereqs > 0:
        allow_skip_percent = (missing_prereqs / total_prereqs) * 100
    else:
        allow_skip_percent = 0
    
    return {
        'recommended_courses': recommended_courses,
        'prerequisites': all_prerequisites,
        'missing_prerequisites': missing_prerequisites,
        'allow_skip_percent': allow_skip_percent
    }
