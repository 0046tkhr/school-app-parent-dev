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
    parent_id = Column('parent_id', Integer, comment='保護者ID')
    last_name = Column('last_name', String(30), comment='氏名（姓）')
    last_name_kana = Column('last_name_kana', String(30), comment='氏名カナ（姓）')
    first_name = Column('first_name', String(30), comment='氏名（名）')
    first_name_kana = Column('first_name_kana', String(30), comment='氏名カナ（名）')
    number = Column('number', Integer, comment='出席番号')
    created_at = Column('created_at', DATETIME, comment='作成日')
    updated_at = Column('updated_at', DATETIME, comment='更新日')
    last_updated_by = Column('last_updated_by', String(30), comment='最終更新者')
    classroom_id = Column('classroom_id', Integer, ForeignKey("m_classroom.classroom_id"), comment='クラスID')
    security_key = Column('security_key', String(8), comment='セキュリティーキー')
    
    # 外部制約
    classroom = relationship("Classroom", back_populates="students", foreign_keys=[classroom_id])
    
    def to_dict_relationship(self):
        model = self.to_dict()
        if self.classroom is not None:
            model["classroom"] = self.classroom.to_dict()
        return model
    def query_to_dict_relationship(result):
        # 変数を初期化する
        items = []
        # 結果を処理する
        for row in result:
            model = row.to_dict_relationship()
            items.append(model)
        return items