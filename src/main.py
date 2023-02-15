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

# import json
import hashlib

import boto3

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
    response = {
        "statusCode": 200,
    }
    return response

@app.route("/api/schoolappParent/login", methods=["POST"])
def login():
    print('login')
    event = request.get_json()

    # ログイン情報の取得
    id = event['id']
    password = event['password']

    # パスワードのハッシュ化
    password_hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # ログイン情報から、紐づく保護者を検索
    parent_info = {}
    with session_scope() as session:
        parent = session.query(Parents).\
            filter(Parents.parent_id == id, Parents.password == password_hashed).\
            first()

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
    parentInfo = ""
    with session_scope() as session:
        parent = session.query(Parents).\
            filter(Parents.user_id == userId).\
            first()
        if parent:
            parentInfo = {
                "parent_id": parent.parent_id,
                "parent_name": parent.parent_name,
                "relationship_code": parent.relationship_code,
                "user_id": parent.user_id
            }

    # 保護者の情報を返却
    print("parentInfo", parentInfo)
    return {
        "parentInfo": parentInfo
    }

@app.route("/api/schoolappParent/searchStudentsByParentId", methods=["POST"])
def searchStudentByParentId():
    print('searchStudentByParentId')
    # userIdの取得
    event = request.get_json()
    print("event", event)
    parent_id = event['parentId']
    print('parent_id', parent_id)
    
    # parentIdに紐づく生徒情報を全て取得
    student_info_list = []
    with session_scope() as session:
        students = session.query(Students).\
            filter(Students.parent_id == parent_id).\
            all()
        for student in students:
            student_info_list.append({
                "student_id": student.student_id,
                "school_id": student.school_id,
                "parent_id": student.parent_id,
                "last_name": student.last_name,
                "last_name_kana": student.last_name_kana,
                "first_name": student.first_name,
                "first_name_kana": student.first_name_kana,
                "number": student.number,
                "classroom_id": student.classroom_id,
                "security_key": student.security_key
            })

    # 生徒情報を返却
    return {
        "students": student_info_list
    }

@app.route("/api/schoolappParent/linkRelation", methods=["POST"])
def link_relation():
    print('link_relation')
    
    # eventから各値を取得
    event = request.get_json()
    print('event')
    parent_id = event['parentId']
    print('parent_id', parent_id)
    security_key = event['securityKey']
    print('security_key', security_key)
    
    # 生徒情報テーブルの該当レコードを更新
    with session_scope() as session:
        student = session.query(Students).\
            filter(Students.security_key == security_key).\
            first()
        # 保護者情報とまだ紐づいていないなら新規紐づけ
        if not student.parent_id:
            student.parent_id = parent_id
        else:
            return {
                "statusCode": 500
            }
    session.commit()
    
    return {
        "statusCode": 200
    }

@app.route("/api/schoolappParent/searchDelivery", methods=["POST"])
def search_delivery():
    print('search_delivery')
    dynamodb = boto3.resource('dynamodb')

    # リクエストから値を取得
    event = request.get_json()
    parent_id = event['parent_id']
    student_id = event['student_id']

    # 生徒に紐づく配信idのリストを取得
    TABLE_DELIVERY_RELATION = os.environ['TABLE_DELIVERY_RELATION']
    table = dynamodb.Table(TABLE_DELIVERY_RELATION)
    print("table", table)
    try:
        print("start")
        db_response = table.get_item(Key={ "parent_id": parent_id, "student_id": student_id })
        print("db_response", db_response)

        if "Item" in db_response:
            print("鼠")
            item = db_response["Item"]
            print("牛")
            delivery_id_list = item['delivery_id']
        else:
            print("虎")
            return {
                "statusCode": 500,
                "message": "db result not found"
            }
    except Exception as error:
        print("兎", error)
        return {
            "statusCode": 500,
            "error": str(error)
        }

    print("delivery_id_list", delivery_id_list)
    # 配信idに紐づく配信情報のリストを取得
    TABLE_DELIVERY_HISTORY = os.environ['TABLE_DELIVERY_HISTORY']
    table = dynamodb.Table(TABLE_DELIVERY_HISTORY)
    deliveries = []
    for delivery_id in delivery_id_list:
        try:
            db_response = table.get_item(Key={ "delivery_id": delivery_id })
            if "Item" in db_response:
                print("龍")
                item = db_response["Item"]
                deliveries.append(item)
        except Exception as error:
            print("蛇", error)
            return {
                "statusCode": 500,
                "error": str(error)
            }

    print("deliveries", deliveries)
    return {
        "statusCode": 200,
        "deliveries": deliveries
    }