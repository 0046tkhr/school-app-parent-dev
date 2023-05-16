from sqlalchemy import *
from sqlalchemy.orm import *
from database_setting import Base

class AbsenceForm(Base):
    """
    欠席連絡情報
    """
    __tablename__ = 'm_absence_form'
    # テーブルのコメント
    __table_args__ = {
        'comment': '欠席連絡を管理する'
    }
    # テーブルのカラム
    absence_id = Column('absence_id', String(8), primary_key=True, comment='欠席連絡ID')
    parent_id = Column('parent_id', String(9), comment='保護者ID')
    student_id = Column('student_id', String(12), comment='生徒ID')
    reason = Column('reason', String(32), comment='欠席/遅刻理由')
    absence_at = Column('absence_at', Date, comment='欠席/遅刻する日付')
    created_at = Column('created_at', DateTime, comment='作成日')
    form_type = Column('form_type', String(8), comment='連絡の種類(欠席/遅刻)')
    other_reason = Column('other_reason', String(256), comment='その他を選んだ際の欠席/遅刻理由')
    arrive_at = Column('arrive_at', Time, comment='遅刻する時間')
    remarks = Column('remarks', String(256), comment='備考')

    # 外部キー

    # 外部制約設定

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