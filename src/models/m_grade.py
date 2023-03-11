from sqlalchemy import *
from sqlalchemy.orm import *
from database_setting import Base

class Grade(Base):
    """
    学年管理
    """
    __tablename__ = 'm_grade'

    # テーブルのコメント
    __table_args__ = {
        'comment': '学年を管理する'
    }

    # テーブルのカラム
    grade_id = Column('grade_id', Integer, primary_key=True, comment='クラスルームID')
    school_grade = Column('school_grade', String(30), comment='学年')
    school_id = Column('school_id', String(30), comment='学校ID')
    # TODO 外部キーを設定する
    # customer_id = Column('customer_id', Integer, ForeignKey("customers.customer_id"), comment='得意先ID')
    # customer_id = Column('customer_id', Integer, comment='得意先ID')

    # TODO 外部制約設定する
    # students = relationship("Student", back_populates="classroom")

    def query_to_dict_relationship(result):
        # 変数を初期化する
        items = []

        # 結果を処理する
        for row in result:
            items.append({
                'grade_id' : row.grade_id,
                'school_grade' : row.school_grade,
                'school_id' : row.school_id,
            })
            
        return items
    
    def query_to_dict_all_class(result):
        # 変数を初期化する
        items = []
        # 結果を処理する
        for row in result:
            items.append({
                'grade_id' : row.grade_id,
                'school_grade' : row.school_grade,
                'school_id' : row.school_id,
            })            
        return items