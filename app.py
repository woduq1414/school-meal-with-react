import sys



from api.db import db
from flask import blueprints

from flask import render_template, g, Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS


# app = Flask(__name__, static_folder='./static', template_folder='./static')
#app = Flask(__name__)


from flask import Flask

# from . import db
from api import meal_api











def create_app():
    app = Flask(__name__)

    import os
    import subprocess
    import socket
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('FLASK_TEST_DB', None)
    if socket.gethostname() == 'DESKTOP-32A6L4O':
        app.config['SQLALCHEMY_DATABASE_URI'] = \
        subprocess.getstatusoutput('heroku config:get DATABASE_URL -a school-meal-with-react')[1]
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', None)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



    db.init_app(app)


    app.register_blueprint(meal_api, url_prefix='')
    return app





if __name__ == '__main__':
    app = create_app()


    # Because this is just a demonstration we set up the database like this.

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

    app.run(debug=True, host='127.0.0.1', port=5000)



CORS(app)





#
#
# if __name__ == '__main__':
#     app.run(debug=True, host='127.0.0.1', port=5000)









