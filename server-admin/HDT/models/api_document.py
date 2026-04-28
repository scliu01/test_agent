from datetime import datetime
from app import database


class ApiDocument(database.Model):
    __tablename__ = 'api_documents'

    id = database.Column(database.Integer, primary_key=True)
    project_id = database.Column(database.Integer, nullable=False)
    name = database.Column(database.String(255))
    parent_id = database.Column(database.Integer)
    sort_order = database.Column(database.Integer, default=0, comment='排序字段')
    is_directory = database.Column(database.Boolean, default=False, nullable=False)
    title = database.Column(database.String(255))
    content = database.Column(database.Text)
    ai_suggest = database.Column(database.Text)
    created_by = database.Column(database.Text, default='system')
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'is_directory': self.is_directory,
            'title': self.title,
            'content': self.content,
            'ai_suggest': self.ai_suggest,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
