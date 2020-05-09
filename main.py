# -*- coding: utf-8 -*-
from datetime import timedelta
from flask import Flask, session, app, request
from main import index
from user import user
from board import board_list
from store import store
from my_page import my_page
from message import message_python
from game_center import game_center
from admin import admin_class as ac
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, logout_user, UserMixin
from sql_info import mysql_info

mysql = mysql_info.info

app = Flask(__name__, template_folder='view', static_url_path='', static_folder='static')

app.secret_key = '시크릿_키_발급'

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+mysql['user']+':'+mysql['password']+'@'+mysql['host']+'/'+mysql['db']
app.config['SECRET_KEY'] = 'sfkjlrgnvrefiovnoi'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# set flask_admin 

db = SQLAlchemy(app)

login = LoginManager(app)

class member(db.Model, UserMixin) :
    
    mem_no = db.Column(db.Integer, primary_key = True)
    mem_id = db.Column(db.String(30))
    mem_nic = db.Column(db.String(30))
    mem_gold = db.Column(db.Integer)
    mem_silver = db.Column(db.Integer)
    mem_mil = db.Column(db.Integer)
    mem_admin = db.Column(db.Integer)
    
    def get_id(self):
        return (self.mem_no)

class gold_detail(db.Model) :
    gld_usage = db.Column(db.Integer, primary_key=True)
    usage_detail = db.Column(db.String(30))

class gold_report(db.Model, UserMixin) :
    
    gld_no = db.Column(db.Integer, primary_key = True)
    mem_no = db.Column(db.Integer, db.ForeignKey('member.mem_no'))
    gld_date = db.Column(db.Integer)
    gld_price = db.Column(db.Integer)
    gld_usage = db.Column(db.Integer, db.ForeignKey('gold_detail.gld_usage'))
    user = db.relationship('member', foreign_keys=mem_no, backref='gold_reports')
    usage = db.relationship('gold_detail', foreign_keys=gld_usage)
    def get_id(self):
        return (self.mem_no)

class silver_detail(db.Model) :
    slv_usage = db.Column(db.Integer, primary_key=True)
    usage_detail = db.Column(db.String(30))

class silver_report(db.Model, UserMixin) :
    
    slv_no = db.Column(db.Integer, primary_key = True)
    mem_no = db.Column(db.Integer, db.ForeignKey('member.mem_no'))
    slv_date = db.Column(db.Integer)
    slv_price = db.Column(db.Integer)
    slv_usage = db.Column(db.Integer, db.ForeignKey('silver_detail.slv_usage'))
    user = db.relationship('member', foreign_keys=mem_no, backref='silver_reports')
    usage = db.relationship('silver_detail', foreign_keys=slv_usage)
    def get_id(self):
        return (self.mem_no)

class mileage_detail(db.Model) :
    mil_usage = db.Column(db.Integer, primary_key=True)
    usage_detail = db.Column(db.String(30))

class mileage_report(db.Model, UserMixin) :
    
    mil_no = db.Column(db.Integer, primary_key = True)
    mem_no = db.Column(db.Integer, db.ForeignKey('member.mem_no'))
    mil_date = db.Column(db.Integer)
    mil_price = db.Column(db.Integer)
    mil_usage = db.Column(db.Integer, db.ForeignKey('mileage_detail.mil_usage'))
    user = db.relationship('member', foreign_keys=mem_no, backref='mileage_reports')
    usage = db.relationship('mileage_detail', foreign_keys=mil_usage)
    def get_id(self):
        return (self.mem_no)

class message(db.Model) :
    mess_no = db.Column(db.Integer, primary_key = True)
    mess_text = db.Column(db.String(255))
    mess_date = db.Column(db.DateTime)
    sender_no = db.Column(db.Integer, db.ForeignKey('member.mem_no'))
    receiver_no = db.Column(db.Integer, db.ForeignKey('member.mem_no'))
    mess_readtime = db.Column(db.DateTime)
    sender = db.relationship('member', foreign_keys=sender_no)
    receiver = db.relationship('member', foreign_keys=receiver_no)
    def get_id(self):
        return (self.mem_no)

class betting(db.Model) :
    bet_no = db.Column(db.Integer, primary_key=True)
    mem_no = db.Column(db.Integer, db.ForeignKey('member.mem_no'))
    bet_date = db.Column(db.DateTime)
    bet_gold = db.Column(db.Integer)
    bedang = db.Column(db.Integer)
    result = db.Column(db.Integer, db.ForeignKey('betting_status.status_no')) 
    user = db.relationship('member', foreign_keys=mem_no)
    result_info = db.relationship('betting_status', foreign_keys=result)
    def get_id(self):
        return (self.mem_no)

class betting_info(db.Model) :
    betting_info_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

class betting_status(db.Model) :
    status_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))


class game_class(db.Model) :
    game_class = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

class betting_detail(db.Model) :
    bet_no = db.Column(db.Integer, db.ForeignKey('betting.bet_no'))
    game_class = db.Column(db.Integer, db.ForeignKey('game_class.game_class'))
    game_date = db.Column(db.DateTime)
    home = db.Column(db.String(30))
    away = db.Column(db.String(30))
    
    result = db.Column(db.Integer, db.ForeignKey('betting_status.status_no'))
    standard = db.Column(db.Integer)
    betting = db.Column(db.Integer, db.ForeignKey('betting_info.betting_info_no'))
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    betting_detail_pk = db.Column(db.Integer, primary_key=True)
    
    bet = db.relationship('betting', foreign_keys=bet_no)
    game_class_info = db.relationship('game_class', foreign_keys=game_class)
    result_info = db.relationship('betting_status', foreign_keys=result)
    betting_info = db.relationship('betting_info', foreign_keys=betting)

@login.user_loader
def load_user(mem_no) :
    
    return member.query.get(1)


admin = Admin(app, name='prediction', template_mode='bootstrap3', index_view = ac.MyAdminIndexView())

admin.add_view(ac.member_modelView(member, db.session, name="유저 관리"))
admin.add_view(ac.gold_modelView(gold_report, db.session, name="골드 관리", category="재화 관리"))
admin.add_view(ac.silver_modelView(silver_report, db.session, name="은화 관리", category="재화 관리"))
admin.add_view(ac.mileage_modelView(mileage_report, db.session, name="마일리지 관리", category="재화 관리"))
admin.add_view(ac.message_modelView(message, db.session, name="쪽지 관리"))
admin.add_view(ac.betting(betting, db.session, name="베팅", category="베팅 관리"))
admin.add_view(ac.betting_detail(betting_detail, db.session, name="베팅 상세", category="베팅 관리"))

admin.add_view(ac.AnalyticsView(name='Analytics', endpoint='analytics'))

@app.route('/admin_login_pro', methods = ['post'])
def admin_login() :
    
    id = request.form['user_id']
    pw = request.form['user_pw']
    
    if id == 'prediction' and pw == 'admin0508!' :
        
        mem_id = member.query.get(1)
        login_user(mem_id)
        return 'YES'
    else :
        return 'NO'

@app.route('/admin/logout')
def amdin_logout() :
    logout_user()
    return 'Logged Out'

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)


app.register_blueprint(index.main_blue)
app.register_blueprint(user.user_blue)
app.register_blueprint(board_list.board_blue)
app.register_blueprint(store.store_blue)
app.register_blueprint(my_page.my_blue)
app.register_blueprint(message_python.message_blue)
app.register_blueprint(game_center.game_blue)

app.run(host='0.0.0.0', port = 5000)

