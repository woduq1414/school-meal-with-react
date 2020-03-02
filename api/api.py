from flask import Flask
from flask_restful import Resource, Api, reqparse
import requests, json
import datetime
import re
import sqlalchemy
import numpy as np
import itertools
from celery import Celery
from threading import Thread
import asyncio

app = Flask(__name__, static_url_path='', static_folder='../static', template_folder='../static')
app.config['CELERY_BROKER_URL'] = "redis://localhost:6379"


api = Api(app)

from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name, backend="redis://localhost:6379",
                    broker="redis://localhost:6379")
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)

from api.db import *
from api.model import *

"""
http://127.0.0.1:5000/schools/디지털
http://127.0.0.1:5000/api/meals/J100000855/month/20190908
http://127.0.0.1:5000/api/meals/J100000855/week/20190908
http://127.0.0.1:5000/api/meals/J100000855/day/20190908
"""


def remove_allergy(str):
    return re.sub("[0-9]*\.", '', str)


def get_region_code(school_code):
    t = school_code[0]
    return {"B": "sen.go", "C": "pen.go", "D": "dge.go", "E": "ice.go", "F": "gen.go", "G": "dje.go", "H": "use.go",
            "I": "sje.go", "J": "goe.go",
            "K": "kwe.go", "M": "cbe.go", "N": "cne.go", "P": "jbe.go", "Q": "jne.go", "R": "gbe", "S": "gne.go",
            "T": "jje.go"}[t]


class DB(Resource):
    def get(self):

        # @celery.task()
        # def add_together(a, b):
        #     import time
        #     time.sleep(5)
        #     print(a + b)
        # add_together(3,5)

        def do_work(a,b):
            # do something that takes a long time
            import time
            time.sleep(3)
            print(a+b)


        thread = Thread(target=do_work, kwargs={'a': 3, 'b': 5})
        thread.start()
        return "hello"
    # def get(self, postSeq):
    #     try:
    #         post = Board.query.filter_by(postSeq=postSeq).one()
    #
    #
    #     except sqlalchemy.orm.exc.NoResultFound:
    #         return {"message": "존재하지 않는 게시글 입니다."}, 404
    #
    #     post.hit = post.hit + 1
    #     db.session.commit()
    #     return {
    #                "data": {
    #                    "postSeq": post.postSeq,
    #                    "userId": post.userId,
    #                    "userName": post.userNickname,
    #                    "title": post.title,
    #                    "postDate": str(post.postDate),
    #                    "hit": post.hit
    #                }
    #            }, 200


class SearchSchoolName(Resource):
    def get(self, school_name):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int)
        args = parser.parse_args()

        limit = args["limit"]

        if limit is None:
            limit = 100

        with requests.Session() as s:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
            form = {
                "HG_CD": "",
                "SEARCH_KIND": "",
                "HG_JONGRYU_GB": "",
                "GS_HANGMOK_CD": "",
                "GS_HANGMOK_NM": "",
                "GU_GUN_CODE": "",
                "SIDO_CODE": "",
                "GUGUN_CODE": "",
                "SRC_HG_NM": school_name
            }
            school_page = s.post('https://www.schoolinfo.go.kr/ei/ss/Pneiss_a01_l0.do', data=form, headers=headers)

            data = school_page.text
            data = json.loads(data, encoding="utf-8")

            result = []
            # return data
            for school_type, schools in data.items():

                for school in schools:

                    if len(result) >= limit:
                        break;

                    if school_type == "schoolList02":
                        type = "초등"
                    elif school_type == "schoolList03":
                        type = "중등"
                    elif school_type == "schoolList04":
                        type = "고등"
                    result.append({
                        "schoolType": type,
                        "schoolRegion": school['LCTN_NM'],
                        "schoolAddress": school['SCHUL_RDNMA'] if "SCHUL_RDNMA" in school else "주소를 찾을 수 없습니다.",
                        "schoolName": school['SCHUL_NM'],
                        "schoolCode": school["SCHUL_CODE"]
                    })

            if result:

                def InsertSchoolsDB(result, limit):
                    now = datetime.datetime.now()
                    # result[0]['insertDate'] = str(now)
                    result = result[:limit]
                    schools = list()

                    schoolCodes = Schools.query.with_entities(Schools.schoolCode).all()
                    schoolCodes = list((itertools.chain.from_iterable(schoolCodes))) # flatten

                    for school in result:

                        if school["schoolCode"] not in schoolCodes:
                            schools.append(Schools(**school, insertDate=now))

                        print(school)
                    db.session.add_all(schools)

                    db.session.commit()

                thread = Thread(target= InsertSchoolsDB, kwargs={'result': result, 'limit': limit})
                thread.start()

                return result[:limit], 200
            else:
                return {"message": "학교를 찾을 수 없음"}, 404


class GetSchoolNameWithSchoolCode(Resource):
    def get(self, school_code):
        school = Schools.query.filter_by(schoolCode=school_code).first()
        if school is not None:
            return {
                        "schoolType": school.schoolType,
                        "schoolRegion": school.schoolRegion,
                        "schoolAddress": school.schoolAddress,
                        "schoolName": school.schoolName,
                        "schoolCode": school.schoolCode
                    }
        else:
            return {"message": "학교를 찾을 수 없음"}, 404


class GetMealByMonthFromNeis(Resource):
    def get(self, school_code, target_date):

        with requests.Session() as s:
            first_page = s.get('https://stu.{}.kr/edusys.jsp?page=sts_m40000'.format(get_region_code(school_code)))

            headers = {
                "Content-Type": "application/json"
            }
            payload = {"ay": target_date[0:4], "mm": target_date[4:6], "schulCode": school_code,
                       "schulKndScCode": "02", "schulCrseScCode": "2"}
            payload = json.dumps(payload)
            meal_page = s.post('https://stu.{}.kr/sts_sci_md00_001.ws'.format(get_region_code(school_code)),
                               data=payload, headers=headers,
                               cookies=first_page.cookies)

            data = meal_page.text
            data = json.loads(data, encoding="utf-8")

        mth_diet_list = data["resultSVO"]['mthDietList']
        if not mth_diet_list:
            return {"message": "학교를 찾을 수 없거나, 날짜가 잘못됨."}, 404

        meals = []

        for week_diet_list in mth_diet_list:
            week = {"weekGb": week_diet_list["weekGb"]}
            for day in ["sun", "mon", "tue", "wed", "the", "fri", "sat"]:
                temp = week_diet_list[day]
                if temp is not None:
                    date = temp.split("<br />")
                    if date[0] is not None:
                        week[day] = {"date": date[0], "meal": list(map(remove_allergy, date[2:]))}
            meals.append(week)

        result = {
            'result': {
                "status": data["result"]['status']
            },
            "data": meals
        }
        return result


class GetMealByWeekWithDetailFromNeis(Resource):
    def get(self, school_code, target_date):
        with requests.Session() as s:
            first_page = s.get('https://stu.{}.kr/edusys.jsp?page=sts_m40000'.format(get_region_code(school_code)))

            headers = {
                "Content-Type": "application/json"
            }
            payload = {"schYmd": target_date, "schulCode": school_code,
                       "schulKndScCode": "04", "schulCrseScCode": "4", "schMmealScCode": "2"}
            payload = json.dumps(payload)
            meal_page = s.post('https://stu.{}.kr/sts_sci_md01_001.ws'.format(get_region_code(school_code)),
                               data=payload, headers=headers,
                               cookies=first_page.cookies)

            data = meal_page.text
            data = json.loads(data, encoding="utf-8")
            try:
                week_diet_list = data["resultSVO"]['weekDietList'][-1]
                week_detail_list = data["resultSVO"]['dietNtrList']
            except:
                return {"message": "학교를 찾을 수 없거나, 날짜가 잘못됨."}, 404

            meals = []

            first_date = int(target_date[6:8]) - (datetime.date(int(target_date[0:4]), int(target_date[4:6]),
                                                                int(target_date[6:8])).isoweekday() % 7)

            week = {"weekGb": (first_date - 2) // 7 + 2}
            for i, day in enumerate(["sun", "mon", "tue", "wed", "the", "fri", "sat"]):
                temp = week_diet_list[day]
                if temp is not None:
                    date = temp.split("<br />")
                    if date[0] is not None:
                        week[day] = {"date": first_date + i, "meal": list(map(remove_allergy, date[:-1])), "detail": {}}
                        for ingredient in week_detail_list:
                            week[day]["detail"][ingredient['gb']] = float(ingredient["dy" + str(3 + i)])
                else:
                    week[day] = {"date": first_date + i, "meal": []}
            meals.append(week)

            result = {
                'result': {
                    "status": data["result"]['status']
                },
                "data": meals
            }
            return result


class GetMealByDayWithDetailFromNeis(Resource):
    def get(self, school_code, target_date):
        with requests.Session() as s:
            first_page = s.get('https://stu.{}.kr/edusys.jsp?page=sts_m42310'.format(get_region_code(school_code)))
            headers = {
                "Content-Type": "application/json"
            }
            payload = {"schYmd": target_date, "schulCode": school_code,
                       "schulKndScCode": "04", "schulCrseScCode": "4", "schMmealScCode": "2"}
            payload = json.dumps(payload)
            meal_page = s.post('https://stu.{}.kr/sts_sci_md01_001.ws'.format(get_region_code(school_code)),
                               data=payload, headers=headers)
            data = meal_page.text
            data = json.loads(data, encoding="utf-8")
            try:
                week_diet_list = data["resultSVO"]['weekDietList'][-1]
                week_detail_list = data["resultSVO"]['dietNtrList']
            except:
                return {"message": "학교를 찾을 수 없거나, 날짜가 잘못됨."}, 404

            # return data

            first_date = int(target_date[6:8]) - (datetime.date(int(target_date[0:4]), int(target_date[4:6]),
                                                                int(target_date[6:8])).isoweekday() % 7)

            week = {"weekGb": (first_date - 2) // 7 + 2}
            for i, day in enumerate(["sun", "mon", "tue", "wed", "the", "fri", "sat"]):
                if first_date + i == int(target_date[6:8]):
                    temp = week_diet_list[day]
                    if temp is not None:

                        date = temp.split("<br />")
                        if date[0] is not None:
                            meals = {"date": first_date + i, "meal": list(map(remove_allergy, date[:-1])),
                                     "detail": {}}
                            for ingredient in week_detail_list:
                                meals["detail"][ingredient['gb']] = float(ingredient["dy" + str(3 + i)])
                    else:
                        meals = {"date": first_date + i, "meal": []}
            # meals = week["the"]

            result = {
                'result': {
                    "status": data["result"]['status']
                },
                "data": meals
            }
            return json.loads(json.dumps(result, indent=2))
