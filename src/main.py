import os
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
import boto3
dynamodb = boto3.resource('dynamodb')
TABLE_PARENT_STUDENT_DELIVERY = os.environ['TABLE_PARENT_STUDENT_DELIVERY']

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
    print('dev')
    with session_scope() as session:
        # テーブルを作成する
        # run_migration(session)
        print('p')
        tables = ENGINE.table_names()
        print("tables", tables)
    response = {
        "statusCode": 200,
    }
    return response

@app.route("/api/schoolappParent/login", methods=["POST"])
def login():
    print('login')
    event = request.get_json()
    print('event', event)

    # ログイン情報の取得
    id = event['id']
    password = event['password']
    print('id', id)
    print('password', password)

    # パスワードのハッシュ化
    password_hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
    print('password_hashed', password_hashed)

    # ログイン情報から、紐づく保護者を検索
    with session_scope() as session:
        parent = session.query(Parents).\
            filter(Parents.parent_id == id, Parents.password == password_hashed).\
            first()
        print('parent', parent)

        # 保護者情報として保存
        parent_info = {
            "parent_id": parent.parent_id,
            "school_id": parent.school_id,
            "last_name": parent.last_name,
            "first_name": parent.first_name,
            "last_name_kana": parent.last_name_kana,
            "first_name_kana": parent.first_name_kana,
        }

        # login_codeを用意
        login_code = 1 if parent else 0

    # login_codeが1ならログイン成功
    if login_code == 1:
        response = {
            "statusCode": 200,
            "login_code": login_code,
            "parent_info": parent_info
        }
    else:
        response ={
            "statusCode": 500,
        }
    
    print('response', response)
    return response

@app.route("/api/schoolappParent/searchDelivery", methods=["POST"])
def search_delivery():
    print('search_delivery')
    event = request.get_json()
    print('event', event)
    parent_id = event['parent_id']
    print('parent_id', parent_id)
    student_id = event['student_id']
    print('student_id', student_id)

    # 生徒に紐づく配信情報を取得する
    print("dynamodb", dynamodb)
    print(TABLE_PARENT_STUDENT_DELIVERY)
    table = dynamodb.Table(TABLE_PARENT_STUDENT_DELIVERY)
    print("table", table)
    db_response = "syokiti"
    try:
        db_response = table.get_item(Key={ "parent_id": parent_id, "student_id": student_id })
    except Exception as error:
        print(error)
    print('db_response', db_response)
    if "Item" in db_response:
        item = db_response["Item"]
        print('item', item)
        response = {
            "statusCode": 200,
            "delivery": item['delivery_id']
        }
    else:
        response = {
            "statusCode": 500,
        }
    return response