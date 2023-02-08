from contextlib import contextmanager
import logging
from flask import Flask, request
from flask_cors import CORS
import json
# import requests
# from migrations.migration import run_migration
from database_setting import ENGINE
from database_setting import session
from models.m_parents import *
import hashlib

@contextmanager
def session_scope():
    try:
        yield session  # with asでsessionを渡す
        session.commit()  # 何も起こらなければcommit()
    except:
        session.rollback()  # errorが起こればrollback()
        raise
    finally:
        session.close()  # どちらにせよ最終的にはclose()
# controllerを登録
# app.register_blueprint(CustomerController.app)
app = Flask(__name__)
# CORSを許可する
CORS(app)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
@app.route("/api/schoolappParent/dev", methods=["GET"])
def migration():
    with session_scope() as session:
        # テーブルを作成する
        # run_migration(session)
        print('p')
        tables = ENGINE.table_names()
        print("tables", tables)
        parents= session.query(Parents).all()
        for parent in parents:
            print(parent.last_name + parent.first_name)
    response = {
        "statusCode": 200,
    }
    return response
@app.route("/api/schoolappParent/login", methods=["POST"])
def login():
    event = request.get_json()
    # event = json.loads(request.data, strict=False)
    print('event', event)
    id = event['id']
    password = event['password']
    password_hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
    print('password_hashed', password_hashed)
    with session_scope() as session:
        # テーブルを作成する
        # run_migration(session)
        print('p')
        table_name = ENGINE.table_names()
        print("table_name", table_name)
        # parents = session.query(Parents).all()
        parents = session.query(Parents).\
            filter(Parents.parent_id == id, Parents.password == password_hashed).\
            all()
        print("parents", parents)
        for parent in parents:
            print("parent", parent.last_name + parent.first_name)
        if len(parents) > 0:
            login_code = 1
        else:
            login_code = 0
    response = {
        "statusCode": 200,
        "data": {
            "login_code": login_code,
        }
    }
    return response