import sys
from api.api import GetMealByMonthFromNeis, GetMealByWeekWithDetailFromNeis, GetMealByDayWithDetailFromNeis, \
    SearchSchoolName, DB, GetSchoolNameWithSchoolCode, GetMealStat

from api.api import app, api, db




from flask import render_template, g, Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS


# app = Flask(__name__, static_folder='./static', template_folder='./static')
#app = Flask(__name__)



CORS(app)

api.add_resource(SearchSchoolName, '/api/schools/name/<school_name>')
api.add_resource(GetSchoolNameWithSchoolCode, '/api/schools/code/<school_code>')
api.add_resource(GetMealByMonthFromNeis, '/api/meals/<school_code>/month/<target_date>')
api.add_resource(GetMealByWeekWithDetailFromNeis, '/api/meals/<school_code>/week/<target_date>')
api.add_resource(GetMealByDayWithDetailFromNeis, '/api/meals/<school_code>/day/<target_date>')
api.add_resource(GetMealStat, '/api/meals/stat/<school_code>')
api.add_resource(DB, '/api/db')




# routing > react_router (method = GET)
@app.route('/', defaults={'path': ''}, methods=['GET'])
# @app.route('/<string:path>', methods=['GET'])
def catch_all(path):
    g.jinja2_test = 'jinja2 template working!'
    return render_template('index.html')

# 404 not found > react_router
@app.errorhandler(404)
def not_found(error):
    print("SDF")


    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
