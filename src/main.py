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
from models.m_grade import *
from models.t_delivery_history import *
from models.m_security_key import *

# import json
import hashlib

import datetime

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

# @app.route("/api/schoolappParent/login", methods=["POST"])
# def login():
#     print('login')
#     event = request.get_json()

#     # ログイン情報の取得
#     id = event['id']
#     password = event['password']

#     # パスワードのハッシュ化
#     password_hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()

#     # ログイン情報から、紐づく保護者を検索
#     parent_info = {}
#     with session_scope() as session:
#         parent = session.query(Parents).\
#             filter(Parents.parent_id == id, Parents.password == password_hashed).\
#             first()

#         # 保護者情報として保存
#         parent_info = {
#             "parent_id": parent.parent_id,
#             "school_id": parent.school_id,
#             "last_name": parent.last_name,
#             "first_name": parent.first_name,
#             "last_name_kana": parent.last_name_kana,
#             "first_name_kana": parent.first_name_kana,
#             "uid_1": parent.uid_1,
#             "uid_2": parent.uid_2
#         }

#         # login_codeを用意
#         login_code = 1 if parent else 0

#     # 保護者情報から、紐づく生徒を検索
#     with session_scope() as session:
#         students = session.query(Students).\
#             filter(Students.parent_id == parent_info['parent_id']).\
#             all()

#         # 保護者情報に追加
#         parent_info['students'] = []
#         for student in students:
#             parent_info['students'].append({
#                 "student_id": student.student_id,
#                 "class_name": student.class_name,
#                 "grade": student.grade,
#                 "number": student.number,
#                 "last_name": student.last_name,
#                 "first_name": student.first_name,
#                 "last_name_kana": student.last_name_kana,
#                 "first_name_kana": student.first_name_kana,
#             })

#     # login_codeが1ならログイン成功
#     if login_code == 1:
#         response = {
#             "statusCode": 200,
#             "login_code": login_code,
#             "parent_info": parent_info
#         }
#     else:
#         response ={
#             "statusCode": 500,
#         }

#     return response

# 保護者新規作成
@app.route("/api/schoolappParent/createParent", methods=["POST"])
def createParent():
    with session_scope() as session:
        # payloadの取得
        event = request.get_json()
        last_name = event['last_name']
        first_name = event['first_name']
        last_name_kana = event['last_name_kana']
        first_name_kana = event['first_name_kana']
        # relationship_code = event['relationship_code']
        user_id = event['user_id']

        # parent_idの作成

        # P+YYMM＋連番4桁 例：P23030001
        # 年度の下2桁
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        year_start = datetime.datetime(now.year, 4, 1)  # 年度の最初の日を取得（4月1日）
        if now < year_start:  # 現在の日付が年度の最初の日より前の場合、前年度とみなす
            year = now.year - 1
        else:
            year = now.year

        month = now.month

        result = session.query(func.max(Parents.parent_id)).scalar()

        maxGradeId = 0

        if (result is None or len(result) != 12):
            maxGradeId = 0
        else:
            # 最大値から先頭10文字を除いて数値に変換
            maxGradeId = int(result[5:])

        parentIdValue = 'P' + str(year)[-2:] + str(month).zfill(2)
        newParentId = parentIdValue + str(maxGradeId + 1).zfill(4)

        # 保護者マスタにレコードを登録
    
        parent = Parents(
            parent_id = newParentId,
            last_name = last_name,
            first_name = first_name,
            last_name_kana = last_name_kana,
            first_name_kana = first_name_kana,
            # relationship_code = relationship_code,
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
            parentInfo = Parents.to_dict_relationship(parent)

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
        students = session.query(Students, SecurityKey).\
            filter(Students.student_id == SecurityKey.student_id).\
            filter(SecurityKey.parent_id == parent_id).\
            filter(SecurityKey.is_delete == 0).\
            all()
        for student in students:
            student_info_list.append({
                "student_id": student.Students.student_id,
                "school_id": student.Students.school_id,
                # "parent_id": student.Students.parent_id,
                "last_name": student.Students.last_name,
                "last_name_kana": student.Students.last_name_kana,
                "first_name": student.Students.first_name,
                "first_name_kana": student.Students.first_name_kana,
                "number": student.Students.number,
                "classroom_id": student.Students.classroom_id,
                "security_key": student.Students.security_key
            })

    # 生徒情報を返却
    return {
        "students": student_info_list
    }

@app.route("/api/schoolappParent/linkRelation", methods=["POST"])
def linkRelation():
    print('linkRelation')
    # eventから各値を取得
    event = request.get_json()
    parent_id = event['parentId']
    security_key = event['securityKey']
    
    
    # 生徒情報テーブルの該当レコードを更新
    studentInfo = ""
    with session_scope() as session:
        try:
            target_security_key = session.query(SecurityKey).\
                filter(SecurityKey.security_key == security_key).\
                one()
        except:
            # 1件じゃないorセキュリティキーない
            return {
                "statusCode": 500,
                "body" : 'no-security_key'
            }

        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        errFlag = 0

        # 保護者情報とまだ紐づいていないなら新規紐づけ
        if not target_security_key.parent_id:
            if target_security_key.is_delete == 0:
                if target_security_key.expire_time > now:
                    target_security_key.parent_id = parent_id
                else:
                    # 期限切れ
                    errFlag = 1
                    errText = 'out-of-date'
            else:
                # 削除済み
                errFlag = 1
                errText = 'deleted-security-key'
        else:
            # 埋まってる
            errFlag = 1
            errText = 'already-exists'

        if(errFlag == 1):
            return {
                "statusCode": 500,
                "body" : errText
            }

        student = session.query(Students).\
            filter(Students.student_id == target_security_key.student_id).\
            first()

        if student: # studentのparent_id_n 空の場所に挿入する
            if not student.parent_id_1:
                student.parent_id_1 = parent_id
            elif not student.parent_id_2:
                student.parent_id_1 = parent_id
            elif not student.parent_id_3:
                student.parent_id_1 = parent_id
            elif not student.parent_id_4:
                student.parent_id_1 = parent_id
            else:
                return {
                    "statusCode": 500,
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
    limit = event['limit']

    studentInfo = null
    # 生徒の情報を取得(学校, 学年, 組, 出席番号)
    with session_scope() as session:
        student = session.query(Students).\
            join(Classroom, Students.classroom_id == Classroom.classroom_id, isouter = True).\
            filter(Students.student_id == student_id).\
            first()
        studentInfo = Students.to_dict_relationship(student)

    deliveriesInfo = []
    # 指定された件数の学校全体,学年全体,クラス,生徒個人に向けた配信を取得
    with session_scope() as session:
        school_id = studentInfo['school_id']
        grade_id = studentInfo['classroom']['grade_id']
        classroom_id = studentInfo['classroom_id']
        student_id = studentInfo['student_id']

        Grade_target = aliased(Grade)
        Grade_class = aliased(Grade)
        deliveries = (
            session.query(DeliveryHistory,
                DeliveryHistory.delivery_id,
                DeliveryHistory.school_id,
                DeliveryHistory.delivery_name,
                DeliveryHistory.delivery_contents,
                DeliveryHistory.delivery_division,
                DeliveryHistory.target_grade,
                (Grade_target.school_grade).label("grade_name_target_grade"),
                DeliveryHistory.target_class,
                (Grade_class.school_grade).label("grade_name_target_class"),
                (Classroom.school_class).label("classroom_name_target_class"),
                DeliveryHistory.target_student,
                (Students.last_name).label("student_target_last_name"),
                (Students.first_name).label("student_target_first_name"),
                (Students.last_name_kana).label("student_target_last_name_kana"),
                (Students.first_name_kana).label("student_target_first_name_kana"),
                DeliveryHistory.staff_id,
                DeliveryHistory.delivery_schedule,
                DeliveryHistory.created_at,
                DeliveryHistory.updated_at,
                DeliveryHistory.delivered_at,
            )
            .join(Grade_target, DeliveryHistory.target_grade == Grade_target.grade_id, isouter = True)
            .join(Classroom, DeliveryHistory.target_class == Classroom.classroom_id, isouter = True)
            .join(Grade_class, Classroom.grade_id == Grade_class.grade_id, isouter = True)
            .join(Students, DeliveryHistory.target_student == Students.student_id, isouter = True)
            .filter(or_(
                and_(DeliveryHistory.delivery_division == "SCHOOL", DeliveryHistory.school_id == school_id),
                and_(DeliveryHistory.delivery_division == "GRADE", DeliveryHistory.target_grade == grade_id),
                and_(DeliveryHistory.delivery_division == "CLASS", DeliveryHistory.target_class == classroom_id),
                and_(DeliveryHistory.delivery_division == "PERSONAL", DeliveryHistory.target_student == student_id)
            ))
            .order_by(desc(DeliveryHistory.delivered_at))
            .limit(limit)
            .all()
        )
        # to_dict()を使用するとJSON型を解析できない
        for delivery in deliveries:
            deliveriesInfo.append({
                "delivery_id": delivery.delivery_id,
                "school_id": delivery.school_id,
                "delivery_name": delivery.delivery_name,
                "delivery_contents": delivery.delivery_contents,
                "delivery_division": delivery.delivery_division,
                "target_grade": delivery.target_grade,
                "grade_name_target_grade": delivery.grade_name_target_grade,
                "target_class": delivery.target_class,
                "grade_name_target_class": delivery.grade_name_target_class,
                "classroom_name_target_class": delivery.classroom_name_target_class,
                "target_student": delivery.target_student,
                "student_target_last_name": delivery.student_target_last_name,
                "student_target_first_name": delivery.student_target_first_name,
                "student_target_last_name_kana": delivery.student_target_last_name_kana,
                "student_target_first_name_kana": delivery.student_target_first_name_kana,
                "staff_id": delivery.staff_id,
                "delivery_schedule": delivery.delivery_schedule,
                "created_at": delivery.created_at,
                "updated_at": delivery.updated_at,
                "delivered_at": delivery.delivered_at,
            })

    return {
        "statusCode": 200,
        "deliveries": deliveriesInfo
    }

@app.route("/api/schoolappParent/searchMonthDelivery", methods=["POST"])
def search_all_delivery():
    # リクエストから値を取得
    event = request.get_json()
    student_id = event['student_id']
    year = event['year']
    month = event['month']
    
    start_month = {
        "year": year,
        "month": month
    }
    
    end_month = {
        "year": year + 1 if (month == 12) else year,
        "month": 1 if (month == 12) else month + 1 
    }

    studentInfo = null
    # 生徒の情報を取得(学校, 学年, 組, 出席番号)
    with session_scope() as session:
        student = session.query(Students).\
            join(Classroom, Students.classroom_id == Classroom.classroom_id, isouter = True).\
            filter(Students.student_id == student_id).\
            first()
        studentInfo = Students.to_dict_relationship(student)

    deliveriesInfo = []
    # 指定された月の学校全体,学年全体,クラス,生徒個人に向けた配信を取得
    with session_scope() as session:
        school_id = studentInfo['school_id']
        grade_id = studentInfo['classroom']['grade_id']
        classroom_id = studentInfo['classroom_id']
        student_id = studentInfo['student_id']

        Grade_target = aliased(Grade)
        Grade_class = aliased(Grade)
        deliveries = (
            session.query(DeliveryHistory,
                DeliveryHistory.delivery_id,
                DeliveryHistory.school_id,
                DeliveryHistory.delivery_name,
                DeliveryHistory.delivery_contents,
                DeliveryHistory.delivery_division,
                DeliveryHistory.target_grade,
                (Grade_target.school_grade).label("grade_name_target_grade"),
                DeliveryHistory.target_class,
                (Grade_class.school_grade).label("grade_name_target_class"),
                (Classroom.school_class).label("classroom_name_target_class"),
                DeliveryHistory.target_student,
                (Students.last_name).label("student_target_last_name"),
                (Students.first_name).label("student_target_first_name"),
                (Students.last_name_kana).label("student_target_last_name_kana"),
                (Students.first_name_kana).label("student_target_first_name_kana"),
                DeliveryHistory.staff_id,
                DeliveryHistory.delivery_schedule,
                DeliveryHistory.created_at,
                DeliveryHistory.updated_at,
                DeliveryHistory.delivered_at,
            )
            .join(Grade_target, DeliveryHistory.target_grade == Grade_target.grade_id, isouter = True)
            .join(Classroom, DeliveryHistory.target_class == Classroom.classroom_id, isouter = True)
            .join(Grade_class, Classroom.grade_id == Grade_class.grade_id, isouter = True)
            .join(Students, DeliveryHistory.target_student == Students.student_id, isouter = True)
            .filter(and_(
                and_(
                    DeliveryHistory.delivered_at >= datetime.date(start_month['year'], start_month['month'], 1),
                    DeliveryHistory.delivered_at < datetime.date(end_month['year'], end_month['month'], 1)
                ),
                or_(
                    and_(DeliveryHistory.delivery_division == "SCHOOL", DeliveryHistory.school_id == school_id),
                    and_(DeliveryHistory.delivery_division == "GRADE", DeliveryHistory.target_grade == grade_id),
                    and_(DeliveryHistory.delivery_division == "CLASS", DeliveryHistory.target_class == classroom_id),
                    and_(DeliveryHistory.delivery_division == "PERSONAL", DeliveryHistory.target_student == student_id)
                )
            ))
            .order_by(desc(DeliveryHistory.delivered_at))
            .all()
        )

        # to_dict()を使用するとJSON型を解析できない
        for delivery in deliveries:
            deliveriesInfo.append({
                "delivery_id": delivery.delivery_id,
                "school_id": delivery.school_id,
                "delivery_name": delivery.delivery_name,
                "delivery_contents": delivery.delivery_contents,
                "delivery_division": delivery.delivery_division,
                "target_grade": delivery.target_grade,
                "grade_name_target_grade": delivery.grade_name_target_grade,
                "target_class": delivery.target_class,
                "grade_name_target_class": delivery.grade_name_target_class,
                "classroom_name_target_class": delivery.classroom_name_target_class,
                "target_student": delivery.target_student,
                "student_target_last_name": delivery.student_target_last_name,
                "student_target_first_name": delivery.student_target_first_name,
                "student_target_last_name_kana": delivery.student_target_last_name_kana,
                "student_target_first_name_kana": delivery.student_target_first_name_kana,
                "staff_id": delivery.staff_id,
                "delivery_schedule": delivery.delivery_schedule,
                "created_at": delivery.created_at,
                "updated_at": delivery.updated_at,
                "delivered_at": delivery.delivered_at,
            })

    return {
        "statusCode": 200,
        "deliveries": deliveriesInfo
    }