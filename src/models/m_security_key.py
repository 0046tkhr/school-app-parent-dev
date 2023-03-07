from sqlalchemy import *
from sqlalchemy.orm import *
from database_setting import Base

class SecurityKey(Base):
    """
    生徒情報
    """
    __tablename__ = 'm_security_key'

    # テーブルのコメント
    __table_args__ = {
        'comment': 'セキュリティキー情報を管理する'
    }

    # テーブルのカラム
    security_key_id = Column('security_key_id', Integer, primary_key=True, comment='セキュリティキー')
    student_id = Column('student_id', String(14), comment='生徒ID')
    security_key = Column('security_key', String(8), comment='セキュリティキー')
    expire_time = Column('expire_time', DATETIME, comment='有効期限')
    parent_id = Column('parent_id', Integer, comment='保護者id')
    is_delete = Column('is_delete', Integer, comment='削除フラグ')
    
    # TODO 外部制約設定を設定する
    # parent = relationship("Parents", back_populates="students", foreign_keys=[parent_id])

    def to_dict_relationship(self):
        model = self.to_dict()
                        
        return model

    def query_to_dict_relationship(result):
        # 変数を初期化する
        items = []

        # 結果を処理する
        for row in result:
            model = row.to_dict_relationship()
                
            items.append(model)
            
        return items
    
