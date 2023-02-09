import os
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
proxy = os.environ['MYSQL_PROXY_ENDPOINT']
port = os.environ['MYSQL_PORT']
db_name = os.environ['MYSQL_DB_NAME']
user_name = os.environ['MYSQL_USERNAME']
password = os.environ['MYSQL_PASSWORD']
charset_type = "utf8"
# mysqlのDBの設定
DATABASE = f'mysql+mysqlconnector://{user_name}:{password}@{proxy}:{port}/{db_name}?charset={charset_type}'
ENGINE = create_engine(
    DATABASE,
    # encoding = "utf-8",
    echo=False # Trueだと実行のたびにSQLが出力される
)
# Sessionの作成
session = scoped_session(
    # ORM実行時の設定。自動コミットするか、自動反映するなど。
    sessionmaker(
        autocommit = False,
        autoflush = False,
        bind = ENGINE
    )
)
class baseModel(object):
    def to_dict(self):
        model = {}
        for column in self.__table__.columns:
            try:
                # 日付の形式をYYYY/MM/DD HH:MM:SSに変換
                datetime_value = datetime.strptime(str(getattr(self, column.name)), '%Y-%m-%d %H:%M:%S')
                datetime_str = datetime_value.strftime('%Y/%m/%d %H:%M:%S')
            except ValueError:
                # 日付形式でない値はそのまま代入
                model[column.name] = str(getattr(self, column.name))
            else:
                # 日付形式の値はフォーマットした値を代入
                model[column.name] = datetime_str
        return model
    def query_to_dict(result):
        items = []
        for row in result:
            model = row.to_dict() 
            items.append(model)
        return items
# modelで使用する
Base = declarative_base(cls=baseModel)
Base.query = session.query_property()