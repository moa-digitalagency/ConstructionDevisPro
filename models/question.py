from models.base import db, TimestampMixin
from datetime import datetime


class QuestionTemplate(db.Model, TimestampMixin):
    __tablename__ = 'question_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(30), nullable=False)
    options = db.Column(db.JSON)
    default_value = db.Column(db.String(255))
    unit = db.Column(db.String(20))
    is_required = db.Column(db.Boolean, default=True)
    applies_to_rooms = db.Column(db.Boolean, default=False)
    applies_to_project_types = db.Column(db.JSON)
    sort_order = db.Column(db.Integer, default=0)
    help_text = db.Column(db.Text)
    bpu_category_trigger = db.Column(db.String(100))


class ProjectAnswer(db.Model, TimestampMixin):
    __tablename__ = 'project_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question_templates.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    answer_value = db.Column(db.Text)
    answer_data = db.Column(db.JSON)
    is_confirmed = db.Column(db.Boolean, default=False)
    
    project = db.relationship('Project', back_populates='answers')
    question = db.relationship('QuestionTemplate')
    room = db.relationship('Room')
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'question_id', 'room_id', name='uq_project_question_room'),
    )
