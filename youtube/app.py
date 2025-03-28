
from flask import Flask
from config import Config
import os
from models import db
from controllers.upload_controller import upload_bp
from controllers.video_controller import video_bp
from controllers.ui_controller import ui_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    for folder in [app.config['UPLOAD_TEMP_FOLDER'],
                   app.config['UPLOAD_FINAL_FOLDER'],
                   app.config['TRANSCODED_FOLDER']]:
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

    db.init_app(app)
    app.register_blueprint(upload_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(ui_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    application = create_app()
    application.run(debug=True)
