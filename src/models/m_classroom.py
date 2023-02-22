from sqlalchemy import *
from sqlalchemy.orm import *
from database_setting import Base

class Classroom(Base):
    """
    クラス管理
    """
    __tablename__ = 'm_classroom'

    # テーブルのコメント
    __table_args__ = {
        'comment': '生徒を管理する'
    }

    # テーブルのカラム
    classroom_id = Column('classroom_id', Integer, primary_key=True, comment='クラスルームID')
    grade_id = Column('grade_id', String(30), comment='学年')
    school_class = Column('school_class', String(30), comment='クラス')
    # TODO 外部キーを設定する
    # customer_id = Column('customer_id', Integer, ForeignKey("customers.customer_id"), comment='得意先ID')
    # customer_id = Column('customer_id', Integer, comment='得意先ID')

    # 外部キー制約
    students = relationship("Students", back_populates="classroom")

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

    def query_to_dict_class_join_grade(result):
        # 変数を初期化する
        items = []
        # 結果を処理する
        for row in result:
            items.append({
                'classroom_id' : row.classroom_id,
                'school_grade' : row.school_grade,
                'school_class' : row.school_class,
            })            
        return items