from datetime import datetime
from app import database


class TestCase(database.Model):
    __tablename__ = 'test_cases'

    id = database.Column(database.Integer, primary_key=True)
    project_id = database.Column(database.Integer, comment="项目ID")
    module_id = database.Column(database.Integer, comment="模块ID")
    name = database.Column(database.String(255), nullable=False, comment="用例名称")
    priority = database.Column(database.String(10), comment="用例优先级")
    precondition = database.Column(database.String(1024), comment="用例前置条件")
    created_at = database.Column(database.DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = database.Column(database.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    steps = database.Column(database.Text, comment="用例步骤")
    expected = database.Column(database.String(1024), comment="用例预期结果")

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