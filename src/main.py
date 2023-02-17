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
from models.m_classroom import *
from models.t_delivery_history import *

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

    # 登録したレコードを取得
    parentInfo = ""
    with session_scope() as session:
        parent = session.query(Parents).\
            filter(Parents.user_id == user_id).\
            first()
        parentInfo = Parents.to_dict_relationship(parent)

    return {
        "statusCode": 200,
        "parentInfo": parentInfo
    }

@app.route("/api/schoolappParent/searchParentByUserId", methods=["POST"])
def searchParentByUserId():
    # userIdの取得
    event = request.get_json()
    userId = event['userId']
    
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
    return {
        "parentInfo": parentInfo
    }

@app.route("/api/schoolappParent/searchStudentsByParentId", methods=["POST"])
def searchStudentByParentId():
    # userIdの取得
    event = request.get_json()
    parent_id = event['parentId']
    
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
def linkRelation():
    # eventから各値を取得
    event = request.get_json()
    parent_id = event['parentId']
    security_key = event['securityKey']
    
    # 生徒情報テーブルの該当レコードを更新
    studentInfo = ""
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
        studentInfo = Students.to_dict_relationship(student)
    session.commit()
    return {
        "statusCode": 200,
        "student": studentInfo
    }

@app.route("/api/schoolappParent/searchLatestDelivery", methods=["POST"])
def search_latest_delivery():
    # リクエストから値を取得
    event = request.get_json()
    student_id = event['student_id']
    print("student_id",student_id)
    limit = event['limit']
    print("limit", limit)

    studentInfo = null
    # 生徒の情報を取得(学校, 学年, 組, 出席番号)
    with session_scope() as session:
        student = session.query(Students).\
            join(Classroom, Students.classroom_id == Classroom.classroom_id, isouter = True).\
            filter(Students.student_id == student_id).\
            first()
        studentInfo = Students.to_dict_relationship(student)
    print("studentInfo", studentInfo)

    deliveriesInfo = []
    # 学校全体,学年全体,クラス,生徒個人に向けた配信を取得
    with session_scope() as session:
        school_id = studentInfo['school_id']
        print("school_id", school_id)
        grade_id = studentInfo['classroom']['grade_id']
        print("grade_id", grade_id)
        classroom_id = studentInfo['classroom_id']
        print("classroom_id", classroom_id)
        student_id = studentInfo['student_id']
        print("student_id", student_id)

        deliveries = session.query(DeliveryHistory).\
            filter(or_(
                and_(DeliveryHistory.delivery_division == "SCHOOL", DeliveryHistory.school_id == school_id),
                and_(DeliveryHistory.delivery_division == "GRADE", DeliveryHistory.target_grade == grade_id),
                and_(DeliveryHistory.delivery_division == "CLASS", DeliveryHistory.target_class == classroom_id),
                and_(DeliveryHistory.delivery_division == "PERSONAL", DeliveryHistory.target_student == student_id)
            )).\
            order_by(asc(DeliveryHistory.delivered_at)).\
            limit(limit).\
            all()
        deliveriesInfo = deliveriesInfo + DeliveryHistory.query_to_dict_relationship(deliveries)
    print('deliveriesInfo', deliveriesInfo)

    return {
        "statusCode": 200,
        "deliveries": deliveriesInfo
    }

@app.route("/api/schoolappParent/searchMonthDelivery", methods=["POST"])
def search_all_delivery():
    # リクエストから値を取得
    event = request.get_json()
    student_id = event['student_id']
    print("student_id",student_id)
    year = event['year']
    month = event['month']

    studentInfo = null
    # 生徒の情報を取得(学校, 学年, 組, 出席番号)
    with session_scope() as session:
        student = session.query(Students).\
            join(Classroom, Students.classroom_id == Classroom.classroom_id, isouter = True).\
            filter(Students.student_id == student_id).\
            first()
        studentInfo = Students.to_dict_relationship(student)
    print("studentInfo", studentInfo)

    deliveriesInfo = []
    # 学校全体,学年全体,クラス,生徒個人に向けた配信を取得
    with session_scope() as session:
        school_id = studentInfo['school_id']
        print("school_id", school_id)
        grade_id = studentInfo['classroom']['grade_id']
        print("grade_id", grade_id)
        classroom_id = studentInfo['classroom_id']
        print("classroom_id", classroom_id)
        student_id = studentInfo['student_id']
        print("student_id", student_id)

        deliveries = session.query(DeliveryHistory).\
            filter(
                or_(
                    and_(DeliveryHistory.delivery_division == "SCHOOL", DeliveryHistory.school_id == school_id),
                    and_(DeliveryHistory.delivery_division == "GRADE", DeliveryHistory.target_grade == grade_id),
                    and_(DeliveryHistory.delivery_division == "CLASS", DeliveryHistory.target_class == classroom_id),
                    and_(DeliveryHistory.delivery_division == "PERSONAL", DeliveryHistory.target_student == student_id)
                )
            ).\
            order_by(asc(DeliveryHistory.delivered_at)).\
            all()
        deliveriesInfo = deliveriesInfo + DeliveryHistory.query_to_dict_relationship(deliveries)
    print('deliveriesInfo', deliveriesInfo)

    return {
        "statusCode": 200,
        "deliveries": deliveriesInfo
    }