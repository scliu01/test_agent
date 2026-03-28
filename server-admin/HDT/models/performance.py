from datetime import datetime
from app import database


class Performance(database.Model):
    __tablename__ = 'performance'

    id = database.Column(database.Integer, primary_key=True)
    project_id = database.Column(database.Integer, nullable=True)
    configs = database.Column(database.JSON, nullable=True)

    created_at = database.Column(database.TIMESTAMP, default=datetime.utcnow, server_default=database.text('CURRENT_TIMESTAMP'))
    updated_at = database.Column(database.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=database.text('CURRENT_TIMESTAMP'))

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'configs': self.configs,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
