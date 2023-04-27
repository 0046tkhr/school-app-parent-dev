from sqlalchemy import *
from sqlalchemy.orm import *
from database_setting import Base

class DeliveryHistory(Base):
    """
    生徒情報
    """
    __tablename__ = 't_delivery_history'

    # テーブルのコメント
    __table_args__ = {
        'comment': '配信履歴を管理する'
    }

    # テーブルのカラム
    delivery_id = Column('delivery_id', String(32), primary_key=True, comment='配信ID')
    delivery_name = Column('delivery_name', String(255), comment='配信名')
    delivery_contents = Column('delivery_contents', JSON, comment='配信内容')
    delivered_at = Column('delivered_at', DATETIME, comment='配信日')
    delivery_schedule = Column('delivery_schedule', DATETIME, comment='配信予定日')
    created_at = Column('created_at', DATETIME, comment='作成日')
    updated_at = Column('updated_at', DATETIME, comment='更新日')
    school_id = Column('school_id', String(16), comment='学校ID')
    staff_id = Column('staff_id', Integer, comment='配信職員ID')
    delivery_division = Column('delivery_division', String(8), comment='配信区分')
    target_grade = Column('target_grade', Integer, comment='対象学年')
    target_class = Column('target_class', Integer, comment='対象学級')
    target_student = Column('target_student', Integer, comment='対象生徒')
    delivery_status = Column('delivery_status', String(16), comment='配信ステータス')
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