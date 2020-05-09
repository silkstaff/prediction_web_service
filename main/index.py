from flask import Blueprint, render_template, request, session

from user import user_dao

main_blue = Blueprint('main_blue', __name__)

@main_blue.route('/')
def index() :
    html = render_template('index.html')
    return html

@main_blue.route('/admin/login')
def admin_login() :
    
    html = render_template('admin_login.html')
    return html