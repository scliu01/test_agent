from datetime import datetime
# 从app.py中导出数据库对象database
from app import database


# 继续database.Model
class Project(database.Model):
    # 表名称
    __tablename__ = 'projects'

    # 属性名建议与数据库字段名一致
    id = database.Column(database.Integer, primary_key=True) # primary_key=True：表示是表主键
    name = database.Column(database.String(100), nullable=False) # nullable=False：表示不能为空
    description = database.Column(database.Text)
    password = database.Column(database.String(255))
    llm_url = database.Column(database.String(255))
    llm_key = database.Column(database.String(255))  # 修复列名避免MySQL关键字冲突
    llm_model = database.Column(database.String(255))
    lvm_url = database.Column(database.String(255))
    lvm_key = database.Column(database.String(255))  # 修复列名避免MySQL关键字冲突
    lvm_model = database.Column(database.String(255))
    created_at = database.Column(database.DateTime, default=datetime.utcnow) # default=datetime.utcnow：设置默认值
    updated_at = database.Column(database.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # onupdate=datetime.utcnow：设置更新值
    extend_json = database.Column(database.Text)

    # 将数据库中的内容转换成字典
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'password': self.password,
            'llm_url': self.llm_url,
            'llm_key': self.llm_key,
            'llm_model': self.llm_model,
            'lvm_url': self.lvm_url,
            'lvm_key': self.lvm_key,
            'lvm_model': self.lvm_model,
            'extend_json': self.extend_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }