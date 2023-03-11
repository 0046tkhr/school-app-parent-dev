from sqlalchemy import *
from sqlalchemy.orm import *
from database_setting import Base

class Parents(Base):
    """
    保護者情報
    """
    __tablename__ = 'm_parents'
    # テーブルのコメント
    __table_args__ = {
        'comment': '保護者を管理する'
    }
    # テーブルのカラム
    parent_id = Column('parent_id', Integer, primary_key=True, comment='保護者ID')
    last_name = Column('last_name', String(30), comment='保護者氏名(姓)')
    first_name = Column('first_name', String(30), comment='保護者氏名(名)')
    last_name_kana = Column('last_name_kana', String(30), comment='保護者氏名(姓・カナ)')
    first_name_kana = Column('first_name_kana', String(30), comment='保護者氏名(名・カナ)')
    user_id = Column('user_id', String(33), comment='ユーザーID')
    expiration_time = Column('expiration_time', DATETIME, comment='有効期限')
    relationship_code = Column('relationship_code', String(3), comment='続柄コード')
    created_at = Column('created_at', DATETIME, comment='作成日')
    updated_at = Column('updated_at', DATETIME, comment='更新日')
    last_updated_by = Column('last_updated_by', String(30), comment='最終更新者')
    # 外部キー
    # customer_id = Column('customer_id', Integer, ForeignKey("customers.customer_id"), comment='得意先ID')
    # customer_id = Column('customer_id', Integer, comment='得意先ID')
    # 外部制約設定
    # customer = relationship("Customer", back_populates="customerStaffs", foreign_keys=[customer_id])
    
    def to_dict_relationship(self):
        model = self.to_dict()
        print(model)
        return model
    def query_to_dict_relationship(result):
        # 変数を初期化する
        items = []
        # 結果を処理する
        for row in result:
            model = row.to_dict_relationship()
            items.append(model)
        return items