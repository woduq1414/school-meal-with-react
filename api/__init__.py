import logging

from flask import Blueprint
from flask_restful import Api




from .api import *


meal_api = Blueprint('meal_api', __name__, static_url_path='', static_folder='../static', template_folder='../static')




api = Api(meal_api)

# resource map
api.add_resource(SearchSchoolName, '/api/schools/name/<school_name>')
api.add_resource(GetSchoolNameWithSchoolCode, '/api/schools/code/<school_code>')
api.add_resource(GetMealByMonthFromNeis, '/api/meals/<school_code>/month/<target_date>')
api.add_resource(GetMealByWeekWithDetailFromNeis, '/api/meals/<school_code>/week/<target_date>')
api.add_resource(GetMealByDayWithDetailFromNeis, '/api/meals/<school_code>/day/<target_date>')
api.add_resource(GetMealDetailStat, '/api/meals/stat/detail/<school_code>')
api.add_resource(GetMealMenuStat, '/api/meals/stat/menu/<school_code>/<menu>')


@meal_api.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request. %s' % str(e))
    return 'An internal error occurred.', 500