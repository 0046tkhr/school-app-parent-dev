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

@app.route("/api/schoolappParent/searchDelivery", methods=["POST"])
def search_delivery():
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
            "message": "invalid value"
        }
    return response