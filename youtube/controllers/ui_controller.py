
from flask import Blueprint, render_template

ui_bp = Blueprint('ui', __name__, template_folder='templates')

@ui_bp.route('/')
def index():
    return render_template('index.html')
