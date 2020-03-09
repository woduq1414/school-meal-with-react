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
import base64
import asyncio

app = Flask(__name__, static_url_path='', static_folder='../static', template_folder='../static')


api = Api(app)



from api.db import *
from api.model import *

"""
http://127.0.0.1:5000/schools/디지털
http://127.0.0.1:5000/api/meals/J100000855/month/20190908
http://127.0.0.1:5000/api/meals/J100000855/week/20190908
http://127.0.0.1:5000/api/meals/J100000855/day/20190908
"""


def remove_allergy(str):
    temp = re.sub("\([^)]*\)|[0-9]*\.", '', str)
    return re.sub("[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"A-Za-z]+$", "", temp)


def get_region_code(school_code):
    t = school_code[0]
    return {"B": "sen.go", "C": "pen.go", "D": "dge.go", "E": "ice.go", "F": "gen.go", "G": "dje.go", "H": "use.go",
            "I": "sje.go", "J": "goe.go",
            "K": "kwe.go", "M": "cbe.go", "N": "cne.go", "P": "jbe.go", "Q": "jne.go", "R": "gbe", "S": "gne.go",
            "T": "jje.go"}[t]





class SearchSchoolName(Resource):
    def get(self, school_name):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int)
        parser.add_argument('now', type=str)
        parser.add_argument('schoolCode', type=str)
        args = parser.parse_args()

        limit = args["limit"]
        now = args["now"]
        school_code = args["schoolCode"]

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
                    else:
                        type = "특수"

                    result.append({
                        "schoolType": type,
                        "schoolRegion": school['LCTN_NM'],
                        "schoolAddress": school['SCHUL_RDNMA'] if "SCHUL_RDNMA" in school else "주소를 찾을 수 없습니다.",
                        "schoolName": school['SCHUL_NM'],
                        "schoolCode": school["SCHUL_CODE"]
                    })

            if result:

                def InsertSchoolsDB(result, limit, school_code, thread):
                    now = datetime.datetime.now()
                    # result[0]['insertDate'] = str(now)
                    result = result[:limit]

                    if thread is True:
                        schools = list()

                        schoolCodes = Schools.query.with_entities(Schools.schoolCode).all()
                        schoolCodes = list((itertools.chain.from_iterable(schoolCodes)))  # flatten

                        for school in result:

                            if school["schoolCode"] not in schoolCodes:
                                schools.append(Schools(**school, insertDate=now))

                            print(school)
                        db.session.add_all(schools)

                        db.session.commit()

                    else:

                        for school in result:
                            if school["schoolCode"] == school_code:
                                try:
                                    db.session.add(Schools(**school, insertDate=now))
                                    db.session.commit()
                                except:
                                    pass
                                break

                if now is None and school_code is None:
                    thread = Thread(target=InsertSchoolsDB,
                                    kwargs={'result': result, 'limit': limit, 'school_code': None, 'thread': True})
                    thread.start()
                else:
                    print("ghfhfhfhfhf")
                    InsertSchoolsDB(result, limit, school_code, False)

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
        target_school = Schools.query.filter_by(schoolCode=school_code).first()
        if target_school is None:
            return {"message" : "학교를 찾을 수 없음"}, 404
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
                    school = Schools.query.filter_by(schoolCode=school_code).first()
                    # thread = Thread(name=school_code + str(target_year).zfill(2) + str(target_month).zfill(2),
                    #                 target=insert_meals_db,
                    #                 kwargs={'school_code': school_code, 'target_year': target_year,
                    #                         'target_month': target_month, 'school_name': school.schoolName})
                    # thread.start()

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

            school = Schools.query.filter_by(schoolCode=school_code).first()
            # thread = Thread(name=school_code + str(target_year).zfill(2) + str(target_month).zfill(2),
            #                 target=insert_meals_db,
            #                 kwargs={'school_code': school_code, 'target_year': target_year,
            #                         'target_month': target_month, 'school_name': school.schoolName})
            # thread.start()

            return json.loads(json.dumps(result, indent=2))


def insert_meals_db(school_code, school_name, target_year, target_month, r):
    # if not target_month.isdecimal() or target_year.isdecimal():
    #     return

    running_threads = threading.enumerate()
    c = 0
    for thread in running_threads:

        if thread.getName() == school_code + str(target_year).zfill(2) + str(target_month).zfill(2):
            c = c + 1

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

    print("insert end")
    if c >= 2:
        r["data"] = {"row": row, "first": False}
        return

    r["data"] = {"row": row, "first": True}

    return row


def GetMealFromDB(school_code, start_date, last_date):

    target_school = Schools.query.filter_by(schoolCode=school_code).first()
    if target_school is None:
        return
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

    rows = []
    insert_rows = []

    school = Schools.query.filter_by(schoolCode=school_code).first()
    school_name = ""
    if school is None:
        print("SFDaaaaaaaa")
        return {"message": "학교를 찾을 수 없습니다."}, 404
    else:
        school_name = school.schoolName

    threads = []
    results = []
    while target_year < last_year or (target_year == last_year and target_month <= last_month):

        print(target_year, target_month)

        row = Meals.query.filter_by(schoolCode=school_code, year=target_year, month=target_month).first()
        if row is None:
            results.append({"data": ""})
            thread = Thread(name=school_code + str(target_year).zfill(2) + str(target_month).zfill(2),
                            target=insert_meals_db,
                            kwargs={'school_code': school_code, 'target_year': target_year,
                                    'target_month': target_month, 'school_name': school_name, 'r': results[-1]})
            thread.start()
            threads.append(thread)
        else:
            rows.append(row)
        if target_month == 12:
            target_month = 1
            target_year = target_year + 1
        else:
            target_month = target_month + 1

    for thread in threads:
        thread.join()
    print(results)

    commit_rows = []
    t = Meals.query.filter_by(schoolCode=school_code).with_entities(Meals.ukey).all()
    t = list((itertools.chain.from_iterable(t)))  # flatten
    print(t)
    for result in results:

        data = result["data"]

        row = data["row"]
        if row and row.schoolCode + str(row.year).zfill(2) + str(row.month).zfill(2) not in t:

            commit_rows.append(row)
            rows.append(row)
        else:
            row = Meals.query.filter_by(schoolCode=school_code, year=row.year, month=row.month).first()
            rows.append(row)

    def commit_thread(commit_rows):
        for commit_row in commit_rows:
            try:
                print("!")
                db.session.add(commit_row)
                db.session.commit()
            except:
                db.session.rollback()

    thread = Thread(target=commit_thread, kwargs={"commit_rows": commit_rows})
    thread.start()
    # db.session.add_all(commit_rows)
    # db.session.commit()

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", len(rows))

    return rows


class GetMealDetailStat(Resource):
    def get(self, school_code):

        parser = reqparse.RequestParser()

        parser.add_argument('startDate', type=str)
        parser.add_argument('lastDate', type=str)
        args = parser.parse_args()

        start_date = args["startDate"]
        last_date = args["lastDate"]

        rows = GetMealFromDB(school_code, start_date, last_date)
        if rows is None:
            return {"message" : "학교 코드가 잘못됐거나 뭔가 오류"}, 404

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


class GetMealMenuStat(Resource):
    def get(self, school_code, menu):
        from urllib import parse
        import collections

        menu_name = parse.unquote(base64.b64decode(menu).decode('utf-8'))
        print(school_code, menu_name)

        parser = reqparse.RequestParser()

        parser.add_argument('startDate', type=str)
        parser.add_argument('lastDate', type=str)
        args = parser.parse_args()

        start_date = args["startDate"]
        last_date = args["lastDate"]

        rows = GetMealFromDB(school_code, start_date, last_date)
        if rows is None:
            return {"message" : "학교 코드가 잘못됐거나 뭔가 오류"}, 404
        months = [row.meals for row in rows]
        # print(months)

        menus = []
        c = 0
        for month in months:
            target_year = month["year"]
            target_month = month["month"]
            month_data = month["monthData"]
            for week in month_data:

                week_data = week["weekData"]

                for day_data in week_data:
                    target_date = str(target_year).zfill(4) + str(target_month).zfill(2) + str(day_data["day"]).zfill(
                        2)
                    if day_data["meal"] is not None:
                        c = c + 1
                        for menu in day_data["meal"]:
                            menus.append(menu)

        menusCounter = collections.Counter(menus)
        print(menu)
        print(menusCounter)

        menusCounter = sorted(menusCounter.items(), key=(lambda x: x[1]), reverse=True)

        return {
            'result': {
                "status": "success"
            },
            "data": menusCounter,
            "days": c
        }


def max_dict(dict):
    print(dict)
    max_key = max(dict, key=lambda k: dict[k])
    return {"date": max_key, "value": dict[max_key]}


def min_dict(dict):
    min_key = min(dict, key=lambda k: dict[k])
    return {"date": min_key, "value": dict[min_key]}


def average_dict(dict):
    return sum(value for key, value in dict.items()) / len(dict)
