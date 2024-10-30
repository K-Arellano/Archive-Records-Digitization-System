from flask import Blueprint,render_template
from flask_login import login_required, current_user
from app.secure.authorization import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/ards/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('users/dashboard.html')

@admin_bp.route('/records')
@login_required
@admin_required
def records():
    return render_template('users/records.html')

@admin_bp.route('/documents')
@login_required
@admin_required
def documents():
    return render_template('users/documents.html')

@admin_bp.route('/collage&course_manager')
@login_required
@admin_required
def col_course_manager():
    return render_template('users/colcourse.html')

@admin_bp.route('/account/<user>')
@login_required
@admin_required
def account(user):
    return render_template('users/account.html', user = user)

@admin_bp.route('/account_manager')
@login_required
@admin_required
def account_manager():
    return render_template('users/user_control.html')

@admin_bp.route('/trashbin')
@login_required
@admin_required
def trashbin():
    return render_template('users/trashbin.html')

@admin_bp.route('/benchmark')
@login_required
@admin_required
def benchmarker():
    return render_template('admin/benchmarker.html')