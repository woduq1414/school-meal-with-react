from flask import Flask
from flask_restful import Resource, Api, reqparse
import requests, json
import datetime
import re
import sqlalchemy
import numpy as np
import itertools
import calendar
from threading import Thread
import threading
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

        def do_work(a, b):
            # do something that takes a long time
            import time
            time.sleep(3)
            print(a + b)

        thread = Thread(target=do_work, kwargs={'a': 3, 'b': 5})
        thread.start()
        return "hello"


class SearchSchoolName(Resource):
    def get(self, school_name):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int)
        args = parser.parse_args()

        limit = args["limit"]

        if limit is None:
            limit = 30

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
                    schoolCodes = list((itertools.chain.from_iterable(schoolCodes)))  # flatten

                    for school in result:

                        if school["schoolCode"] not in schoolCodes:
                            schools.append(Schools(**school, insertDate=now))

                        print(school)
                    db.session.add_all(schools)

                    db.session.commit()

                thread = Thread(target=InsertSchoolsDB, kwargs={'result': result, 'limit': limit})
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

        if not target_date.isdecimal():
            return


        target_year = int(target_date[0:4])
        target_month = int(target_date[4:6])
        target_day = int(target_date[6:8])
        row = Meals.query.filter_by(year=target_year, month=target_month, schoolCode=school_code).first()
        if row is not None:
            month_data = row.meals["monthData"]
            for weeks in month_data:
                for day_data in weeks["weekData"]:
                    if day_data["day"] == target_day:
                        print(day_data)
                        result = {
                            'result': {
                                "status": "success"
                            },
                            "data": day_data,
                            "d": True
                        }
                        return result

            return {"message": "찾을 수 없음"}, 404

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
                week_diet_list = data["resultSVO"]['weekDietList'][2]
                week_detail_list = data["resultSVO"]['dietNtrList']
            except:
                now = datetime.datetime.now()
                if now.year > int(target_year) or (now.year == int(target_year) and now.month > int(target_month)):
                    thread = Thread(name=school_code + str(target_year).zfill(2) + str(target_month).zfill(2),
                                    target=insert_meals_db,
                                    kwargs={'school_code': school_code, 'target_year': target_year,
                                            'target_month': target_month})
                    thread.start()

                return {"message": "학교를 찾을 수 없거나, 날짜가 잘못됨."}, 404
            # return data

            first_date = int(target_date[6:8]) - (datetime.date(int(target_date[0:4]), int(target_date[4:6]),
                                                                int(target_date[6:8])).isoweekday() % 7)

            week = {"weekGb": (first_date - 2) // 7 + 2}
            for i, dayweek in enumerate(["sun", "mon", "tue", "wed", "the", "fri", "sat"]):
                if first_date + i == int(target_date[6:8]):
                    temp = week_diet_list[dayweek]
                    if temp is not None:

                        date = temp.split("<br />")
                        if date[0] is not None:
                            meals = {"date": first_date + i, "meal": list(map(remove_allergy, date[:-1])),
                                     "detail": {}}
                            for ingredient in week_detail_list:
                                meals["detail"][ingredient['gb']] = float(ingredient["dy" + str(3 + i)])
                    else:
                        meals = {"date": first_date + i, "meal": [], "dayweek": dayweek}
            # meals = week["the"]

            result = {
                'result': {
                    "status": data["result"]['status']
                },
                "data": meals,
                "d": False
            }

            thread = Thread(name=school_code + str(target_year).zfill(2) + str(target_month).zfill(2),
                            target=insert_meals_db,
                            kwargs={'school_code': school_code, 'target_year': target_year,
                                    'target_month': target_month})
            thread.start()

            return json.loads(json.dumps(result, indent=2))


def insert_meals_db(school_code, target_year, target_month):

    # if not target_month.isdecimal() or target_year.isdecimal():
    #     return


    running_threads = threading.enumerate()
    c = 0
    for thread in running_threads:

        if thread.getName() == school_code + str(target_year).zfill(2) + str(target_month).zfill(2):
            c = c + 1

    if c >= 2:
        return

    row = Meals.query.filter_by(schoolCode=school_code, year=target_year, month=target_month).first()
    if row is not None:
        return row

    school = Schools.query.filter_by(schoolCode=school_code).first()
    school_name = ""
    if school is None:
        return
    else:
        school_name = school.schoolName

    with requests.Session() as s:
        first_page = s.get('https://stu.{}.kr/edusys.jsp?page=sts_m42310'.format(get_region_code(school_code)))
        headers = {
            "Content-Type": "application/json"
        }
        month_data = []

        target_day = 1
        while target_day <= calendar.monthrange(target_year, target_month)[1]:

            week_data = []

            target_date = str(target_year).zfill(4) + str(target_month).zfill(2) + str(target_day).zfill(2)
            print(target_date)
            payload = {"schYmd": target_date, "schulCode": school_code,
                       "schulKndScCode": "04", "schulCrseScCode": "4", "schMmealScCode": "2"}
            payload = json.dumps(payload)
            meal_page = s.post('https://stu.{}.kr/sts_sci_md01_001.ws'.format(get_region_code(school_code)),
                               data=payload, headers=headers)
            data = meal_page.text
            data = json.loads(data, encoding="utf-8")

            week_diet_list = {}
            week_detail_list = {}
            try:
                week_diet_list = data["resultSVO"]['weekDietList'][2]
                week_detail_list = data["resultSVO"]['dietNtrList']
            except:
                now = datetime.datetime.now()
                if now.year > int(target_year) or (now.year == int(target_year) and now.month > int(target_month)):

                    week_diet_list = {
                        "sun": "",
                        "mon": "",
                        "tue": "",
                        "wed": "",
                        "the": "",
                        "fri": "",
                        "sat": "",
                    }

                else:
                    return {"message": "학교를 찾을 수 없거나, 날짜가 잘못됨."}, 404

            # return data

            first_date = int(target_date[6:8]) - (datetime.date(int(target_date[0:4]), int(target_date[4:6]),
                                                                int(target_date[6:8])).isoweekday() % 7)

            week_data = {"weekGb": (first_date - 2) // 7 + 2, "weekData": []}
            for i, dayweek in enumerate(["sun", "mon", "tue", "wed", "the", "fri", "sat"]):

                if 1 <= first_date + i <= calendar.monthrange(target_year, target_month)[1]:

                    temp = week_diet_list[dayweek]
                    if temp is not None:

                        date = temp.split("<br />")
                        if date[0] is not None:
                            meals = {"day": first_date + i, "meal": list(map(remove_allergy, date[:-1])),
                                     "dayweek": dayweek}
                            if meals["meal"]:
                                meals["detail"] = {}
                                for ingredient in week_detail_list:
                                    meals["detail"][ingredient['gb']] = float(ingredient["dy" + str(3 + i)])
                            else:
                                meals["meal"] = None
                    else:
                        meals = {"day": first_date + i, "meal": [], "dayweek": dayweek}
                    week_data["weekData"].append(meals)
            # meals = week["the"]

            month_data.append(week_data)

            target_day = target_day + 7
    result = {
        "year": target_year,
        "month": target_month,
        "monthData": month_data
    }

    row = Meals(schoolCode=school_code, schoolName=school_name, year=target_year, month=target_month,
                meals=result, ukey=school_code + str(target_year).zfill(2) + str(target_month).zfill(2),
                insertDate=datetime.datetime.now())
    db.session.add(row)
    try:
        db.session.commit()
    except:
        pass

    print("insert end")
    return row


class GetMealStat(Resource):
    def get(self, school_code):

        parser = reqparse.RequestParser()

        parser.add_argument('startDate', type=str)
        parser.add_argument('lastDate', type=str)
        args = parser.parse_args()

        start_date = args["startDate"]
        last_date = args["lastDate"]

        if not start_date.isdecimal() or not last_date.isdecimal():
            return


        start_year, start_month = int(start_date[0:4]), int(start_date[4:6])
        last_year, last_month = int(last_date[0:4]), int(last_date[4:6])

        now = datetime.datetime.now()
        if last_year > now.year or (last_year == now.year and last_month >= now.month):
            if now.month != 1:
                last_month = now.month - 1
                last_year = now.year
            else:
                last_month = 12
                last_year = now.year - 1

        target_year, target_month = start_year, start_month

        # threads = []
        # while target_year < last_year or (target_year == last_year and target_month <= last_month):
        #
        #     print(target_year, target_month)
        #     thread = Thread(target=insert_meals_db, kwargs={'school_code': school_code, 'target_month': target_month,
        #                                                'target_year': target_year}, name=school_code + str(target_year).zfill(2) + str(target_month).zfill(2))
        #     thread.start()
        #     threads.append(thread)
        #     if target_month == 12:
        #         target_month = 1
        #         target_year = target_year + 1
        #     else:
        #         target_month = target_month + 1
        #
        # for thread in threads:
        #     thread.join()

        rows = []

        while target_year < last_year or (target_year == last_year and target_month <= last_month):

            print(target_year, target_month)
            row = insert_meals_db(school_code, target_year, target_month)
            rows.append(row)
            if target_month == 12:
                target_month = 1
                target_year = target_year + 1
            else:
                target_month = target_month + 1

        months = [row.meals for row in rows]
        print(months)
        details = {}

        for month in months:
            target_year = month["year"]
            target_month = month["month"]
            month_data = month["monthData"]
            for week in month_data:

                week_data = week["weekData"]



                for day_data in week_data:
                    target_date = str(target_year).zfill(4) + str(target_month).zfill(2) + str(day_data["day"]).zfill(
                        2)
                    if "detail" in day_data:
                        for detailName, detailValue in day_data["detail"].items():
                            if detailName in details:
                                details[detailName][target_date] = detailValue
                            else:
                                details[detailName] = {}
                                details[detailName][target_date] = detailValue


        detail_stat = {}

        for detail_name in details:
            detail_stat[detail_name] = {}
            detail_stat[detail_name]["max"] = max_dict(details[detail_name])
            detail_stat[detail_name]["min"] = min_dict(details[detail_name])
            detail_stat[detail_name]["average"] = average_dict(details[detail_name])
        return {
            'result': {
                "status": "success"
            },
            "data": detail_stat

        }



def max_dict(dict):
    print(dict)
    max_key = max(dict, key=lambda k: dict[k])
    return {"date" : max_key, "value" : dict[max_key]}

def min_dict(dict):
    min_key = min(dict, key=lambda k: dict[k])
    return {"date" : min_key, "value" : dict[min_key]}

def average_dict(dict):
    return sum(value for key, value in dict.items()) / len(dict)