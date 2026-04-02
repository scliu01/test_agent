from datetime import datetime
from app import database

class TestCaseExec(database.Model):
    __tablename__ = 'test_cases_exec'
    
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    project_id = database.Column(database.Integer, index=True, comment='项目ID')
    name = database.Column(database.String(255), comment='名称')
    exec_type = database.Column(database.String(255), comment='类型')
    case_ids = database.Column(database.String(2048),  comment='关联用例ID')
    details = database.Column(database.Text, comment='详情')
    desc = database.Column(database.String(1024), comment='简述')
    exec_param = database.Column(database.Text, comment='执行参数')
    exec_status = database.Column(database.String(255), comment='执行状态')
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'exec_type': self.exec_type,
            'case_ids': self.case_ids,
            'details': self.details,
            'desc': self.desc,
            'exec_param': self.exec_param,
            'exec_status': self.exec_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }