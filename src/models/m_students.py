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

    # テーブルのカラム # TODO
    student_id = Column('student_id', String(12), primary_key=True, comment='生徒ID')
    school_id = Column('school_id', String(6), comment='学校ID')
    parent_id_1 = Column('parent_id_1', String(9), comment='保護者ID1')
    parent_id_2 = Column('parent_id_2', String(9), comment='保護者ID2')
    parent_id_3 = Column('parent_id_3', String(9), comment='保護者ID3')
    parent_id_4 = Column('parent_id_4', String(9), comment='保護者ID4')
    last_name = Column('last_name', String(30), comment='氏名（姓）')
    first_name = Column('first_name', String(30), comment='氏名（名）')
    last_name_kana = Column('last_name_kana', String(30), comment='氏名カナ（姓）')
    first_name_kana = Column('first_name_kana', String(30), comment='氏名カナ（名）')
    # parent_id = Column('parent_id', String(8), ForeignKey("m_parents.parent_id"), comment='保護者ID') #TODO 外部キーを設定する
    classroom_id = Column('classroom_id', Integer, ForeignKey("m_classroom.classroom_id"), comment='学年')
    number = Column('number', Integer, comment='出席番号')
    created_at = Column('created_at', DATETIME, comment='作成日')
    updated_at = Column('updated_at', DATETIME, comment='更新日')
    last_updated_by = Column('last_updated_by', String(30), comment='最終更新者')
    security_key = Column('security_key', String(8), comment='セキュリティキー')
    fiscal_year = Column('fiscal_year', Integer, comment='年度')
    is_delete = Column('is_delete', Integer, comment='削除フラグ')
    
    # TODO 外部制約設定する
    classroom = relationship("Classroom", back_populates="students", foreign_keys=[classroom_id])
    
    def to_dict_relationship(self):
        model = self.to_dict()
        print(model)
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
