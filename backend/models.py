from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from datetime import datetime

class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    
    knowledges = db.relationship('StudentKnowledge', back_populates='student')
    cards = db.relationship('StudentCard', back_populates='student')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    time_minutes = db.Column(db.Integer, default=5)  # Time in minutes to complete this card
    
    knowledges = db.relationship('CardKnowledge', back_populates='card')
    courses = db.relationship('CourseCard', back_populates='card')
    student_cards = db.relationship('StudentCard', back_populates='card')

class Knowledge(db.Model):
    __tablename__ = 'knowledges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    theory = db.Column(db.Text)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    
    cards = db.relationship('CardKnowledge', back_populates='knowledge')
    collections = db.relationship('KnowledgeCollection', back_populates='knowledge')
    students = db.relationship('StudentKnowledge', back_populates='knowledge')

class Collection(db.Model):
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    
    knowledges = db.relationship('KnowledgeCollection', back_populates='collection')
    tags = db.relationship('TagCollection', back_populates='collection')

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    estimated_time = db.Column(db.Integer, default=0)  # Total time in minutes to complete the course
    
    cards = db.relationship('CourseCard', back_populates='course')
    tags = db.relationship('TagCourse', back_populates='course')
    required_knowledges = db.relationship('CourseRequiredKnowledge', back_populates='course')
    final_knowledges = db.relationship('CourseFinalKnowledge', back_populates='course')

class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    
    courses = db.relationship('TagCourse', back_populates='tag')
    collections = db.relationship('TagCollection', back_populates='tag')

class StudentCard(db.Model):
    __tablename__ = 'students_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    mark = db.Column(db.Integer)
    
    student = db.relationship('Student', back_populates='cards')
    card = db.relationship('Card', back_populates='student_cards')

class StudentKnowledge(db.Model):
    __tablename__ = 'students_knowledges'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledges.id'), nullable=False)
    quality = db.Column(db.Integer, nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    student = db.relationship('Student', back_populates='knowledges')
    knowledge = db.relationship('Knowledge', back_populates='students')

class CardKnowledge(db.Model):
    __tablename__ = 'cards_knowledges'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledges.id'), nullable=False)
    quality = db.Column(db.Integer, nullable=False)
    
    card = db.relationship('Card', back_populates='knowledges')
    knowledge = db.relationship('Knowledge', back_populates='cards')

class KnowledgeCollection(db.Model):
    __tablename__ = 'knowledges_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledges.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=False)
    
    knowledge = db.relationship('Knowledge', back_populates='collections')
    collection = db.relationship('Collection', back_populates='knowledges')

class CourseCard(db.Model):
    __tablename__ = 'courses_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    
    course = db.relationship('Course', back_populates='cards')
    card = db.relationship('Card', back_populates='courses')

class TagCourse(db.Model):
    __tablename__ = 'tags_courses'
    
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    tag = db.relationship('Tag', back_populates='courses')
    course = db.relationship('Course', back_populates='tags')

class TagCollection(db.Model):
    __tablename__ = 'tags_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=False)
    
    tag = db.relationship('Tag', back_populates='collections')
    collection = db.relationship('Collection', back_populates='tags')

class CourseFinalKnowledge(db.Model):
    __tablename__ = 'courses_final_knowledges'
    
    id = db.Column(db.BigInteger, primary_key=True)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    knowledge_id = db.Column(db.Text, nullable=False)  # Note: This differs from the typical integer foreign key
    quality = db.Column(db.Integer, nullable=False)
    
    course = db.relationship('Course', back_populates='final_knowledges')

class CourseRequiredKnowledge(db.Model):
    __tablename__ = 'courses_required_knowledges'
    
    id = db.Column(db.BigInteger, primary_key=True)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    knowledge_id = db.Column(db.Text, nullable=False)  # Note: This differs from the typical integer foreign key
    quality = db.Column(db.Integer, nullable=False)
    
    course = db.relationship('Course', back_populates='required_knowledges')
