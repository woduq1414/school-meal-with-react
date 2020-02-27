import sys
from api.api import GetMealByMonthFromNeis, GetMealByWeekWithDetailFromNeis, GetMealByDayWithDetailFromNeis, \
    SearchSchoolName
from flask import render_template, g, Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__, static_url_path='', static_folder='./static', template_folder='./static')
api = Api(app)


api.add_resource(SearchSchoolName, '/api/schools/<school_name>')
api.add_resource(GetMealByMonthFromNeis, '/api/meals/<school_code>/month/<target_date>')
api.add_resource(GetMealByWeekWithDetailFromNeis, '/api/meals/<school_code>/week/<target_date>')
api.add_resource(GetMealByDayWithDetailFromNeis, '/api/meals/<school_code>/day/<target_date>')





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
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            app.debug = True
    app.run()
