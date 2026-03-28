from datetime import datetime
from app import database


class TestCase(database.Model):
    __tablename__ = 'test_cases'

    id = database.Column(database.Integer, primary_key=True)
    project_id = database.Column(database.Integer, comment="项目ID")
    module_id = database.Column(database.Integer)
    name = database.Column(database.String(255), nullable=False)
    priority = database.Column(database.String(10))
    precondition = database.Column(database.String(1024))
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    steps = database.Column(database.Text)
    expected = database.Column(database.String(1024))

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'module_id': self.module_id,
            'name': self.name,
            'priority': self.priority,
            'precondition': self.precondition,
            'steps': self.steps,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expected': self.expected
        }