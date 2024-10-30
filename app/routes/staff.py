from flask import Blueprint,render_template
from flask_login import login_required, current_user
from app.secure.authorization import staff_required

staff_bp = Blueprint('staff', __name__, url_prefix='/ards/staff')

@staff_bp.route('/records')
@login_required
@staff_required
def records():
    return render_template('users/records.html')

@staff_bp.route('/documents')
@login_required
@staff_required
def documents():
    return render_template('users/documents.html')

@staff_bp.route('/upload')
@login_required
@staff_required
def upload():
    return render_template('users/upload.html')

@staff_bp.route('/account/<user>')
@staff_required
@login_required
def account(user):
    return render_template('users/account.html', user = user)
