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
    parent_id = Column('parent_id', String(8), primary_key=True, comment='保護者ID')
    school_id = Column('school_id', String(6), comment='学校ID')
    password = Column('password', String(128), comment='パスワード')
    last_name = Column('last_name', String(30), comment='氏名（姓）')
    first_name = Column('first_name', String(30), comment='氏名（名）')
    last_name_kana = Column('last_name_kana', String(30), comment='氏名カナ（姓）')
    first_name_kana = Column('first_name_kana', String(30), comment='氏名カナ（名）')
    uid_1 = Column('uid_1', String(33), comment='UID1')
    uid_2 = Column('uid_2', String(33), comment='UID2')
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