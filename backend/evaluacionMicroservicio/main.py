import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.models import db
from app.routes import evaluation_routes
from flask_cors import CORS 
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    app.config['CORS_HEADERS'] = 'Content-Type,Authorization'
    
    CORS(app, 
         resources={r"/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
         }}, 
         supports_credentials=True)

    db.init_app(app)
    JWTManager(app)
    #with app.app_context():
    #    db.create_all() 
   

    app.register_blueprint(evaluation_routes, url_prefix='/evaluacion')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5003)

