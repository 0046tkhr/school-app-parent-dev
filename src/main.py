import os
from contextlib import contextmanager
import logging

from flask import Flask, request
from flask_cors import CORS
# import requests
# from migrations.migration import run_migration
from database_setting import ENGINE
from database_setting import session
from models.m_parents import *
from models.m_students import *

import json
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
    parent_info = {}
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
            "uid_1": parent.uid_1,
            "uid_2": parent.uid_2
        }

        # login_codeを用意
        login_code = 1 if parent else 0

    # 保護者情報から、紐づく生徒を検索
    with session_scope() as session:
        students = session.query(Students).\
            filter(Students.parent_id == parent_info['parent_id']).\
            all()
        print('students', students)
        # 保護者情報に追加
        parent_info['students'] = []
        for student in students:
            parent_info['students'].append({
                "student_id": student.student_id,
                "class_name": student.class_name,
                "grade": student.grade,
                "number": student.number,
                "last_name": student.last_name,
                "first_name": student.first_name,
                "last_name_kana": student.last_name_kana,
                "first_name_kana": student.first_name_kana,
            })

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

@app.route("/api/schoolappParent/createParent", methods=["POST"])
def createParent():
    print('createParent')
    # payloadの取得
    event = request.get_json()
    parent_name = event['parentName']
    relationship_code = event['relationshipCode']
    user_id = event['userId']

    # 保護者マスタにレコードを登録
    with session_scope() as session:
        parent = Parents(
            parent_name = parent_name,
            relationship_code = relationship_code,
            user_id = user_id
        )
        session.add(parent)
    session.commit()
    return {
        "statusCode": 200
    }

@app.route("/api/schoolappParent/searchParentByUserId", methods=["POST"])
def searchParentByUserId():
    print('searchParentByUserId')
    # userIdの取得
    event = request.get_json()
    userId = event['userId']
    print('userId', userId)
    
    # userIdが一致する保護者を検索
    parentInfo = {}
    with session_scope() as session:
        parent = session.query(Parents).\
            filter(Parents.user_id == userId).\
            first()
        parentInfo = {
            "parent_id": parent.parent_id,
            "parent_name": parent.parent_name,
            "relationship_code": parent.relationship_code,
            "user_id": parent.user_id
        }

    # 保護者の情報を返却
    return {
        "parentInfo": parentInfo
    }

@app.route("/api/schoolappParent/searchStudentsByUserId", methods=["POST"])
def searchParentByUserId():
    print('searchParentByUserId')
    # userIdの取得
    event = request.get_json()
    userId = event['userId']
    print('userId', userId)
    
    # userIdが一致する保護者を検索
    parentInfo = {}
    with session_scope() as session:
        parent = session.query(Parents).\
            filter(Parents.user_id == userId).\
            first()
        parentInfo = {
            "parent_name": parent.parent_name,
            "relationship_code": parent.relationship_code,
            "user_id": parent.user_id
        }

    # 保護者の情報を返却
    return {
        "parentInfo": parentInfo
    }

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