from datetime import datetime
from app import database


class Document(database.Model):
    __tablename__ = 'documents'

    id = database.Column(database.Integer, primary_key=True)
    project_id = database.Column(database.Integer, nullable=False, comment='项目ID')
    name = database.Column(database.String(255), comment="目录名称")
    parent_id = database.Column(database.Integer, comment='父级目录ID')
    is_directory = database.Column(database.Boolean, default=False, nullable=False, comment='是否是目录')
    level = database.Column(database.Integer, default=1, comment='目录层级')
    sort_order = database.Column(database.Integer, default=0, comment='排序字段')
    path = database.Column(database.String(255), nullable=True, comment='节点路径')
    title = database.Column(database.String(255), comment='标题')
    content = database.Column(database.Text, comment='内容')
    ai_suggest = database.Column(database.Text, comment='AI评审建议')
    created_by = database.Column(database.Text, default='system', comment='创建人')
    created_at = database.Column(database.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = database.Column(database.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'parent_id': self.parent_id,
            # 'is_directory': self.is_directory,
            # 'level': self.level,
            'sort_order': self.sort_order,
            # 'path': self.path,
            # 'title': self.title,
            'content': self.content,
            'ai_suggest': self.ai_suggest,
            # 'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
