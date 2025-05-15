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
    
    return render_template('knowledge_detail.html', knowledge=k, quality=quality)
