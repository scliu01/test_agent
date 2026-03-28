from datetime import datetime
from app import database

class TestDataTemplate(database.Model):
    __tablename__ = 'test_data_templates'

    id = database.Column(database.Integer, primary_key=True)
    project_id = database.Column(database.Integer, database.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    name = database.Column(database.String(255), nullable=False)
    description = database.Column(database.Text)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fields = database.Column(database.JSON)
    hint = database.Column(database.Text)
    count = database.Column(database.Integer)
    format = database.Column(database.String(45))
    lang = database.Column(database.String(45))

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'fields': self.fields,
            'hint': self.hint,
            'count': self.count,
            'format': self.format,
            'lang': self.lang
        }