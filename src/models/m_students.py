from sqlalchemy import *
from sqlalchemy.orm import *
from database_setting import Base

class Students(Base):
    """
    生徒情報
    """
    __tablename__ = 'm_students'
    # テーブルのコメント
    __table_args__ = {
        'comment': '生徒を管理する'
    }
    # テーブルのカラム
    student_id = Column('student_id', Integer, primary_key=True, comment='生徒ID')
    school_id = Column('school_id', String(6), primary_key=True, comment='学校ID')
    last_name = Column('last_name', String(30), comment='氏名（姓）')
    first_name = Column('first_name', String(30), comment='氏名（名）')
    last_name_kana = Column('last_name_kana', String(30), comment='氏名カナ（姓）')
    first_name_kana = Column('first_name_kana', String(30), comment='氏名カナ（名）')
    parent_id = Column('parent_id', String(30), comment='保護者ID')
    class_name = Column('class_name', String(30), comment='クラス名')
    grade = Column('grade', Integer, comment='学年')
    number = Column('number', Integer, comment='出席番号')
    created_at = Column('created_at', DATETIME, comment='作成日')
    updated_at = Column('updated_at', DATETIME, comment='更新日')
    last_updated_by = Column('last_updated_by', String(30), comment='最終更新者')