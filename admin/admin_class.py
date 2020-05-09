from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask import redirect, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_admin import Admin, AdminIndexView
from connection.mysql_login import get_connection
import pymysql

class member_modelView(ModelView) :
    can_delete = False
    column_display_pk = True
    column_searchable_list = ['mem_id', 'mem_nic']
    column_filters = ['mem_admin']
    
    def is_accessible(self):
        
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs) :
        return redirect(url_for('admin/login'))


class gold_modelView(ModelView) :
    can_delete = False
    can_edit = False
    column_display_all_relations = True
    column_searchable_list = ['user.mem_nic', 'gld_date','gld_usage', 'usage.usage_detail']
    column_filters = ['user.mem_nic','gld_date', 'usage.usage_detail']
    column_list = ('user.mem_nic', 'gld_date', 'gld_price','gld_usage', 'usage.usage_detail')
    column_exclude_list = ['gld_usage']
    # form_columns = [ 'gld_date', ]
    # column_sortable_list = [('gld_date', True)]
    # column_searchable_list = ['mem_id', 'mem_nic']
    # column_filters = ['mem_admin']
    
    def is_accessible(self):
        
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs) :
        return redirect(url_for('admin/login'))

class silver_modelView(ModelView) :
    can_delete = False
    can_edit = False
    column_display_all_relations = True
    column_searchable_list = ['user.mem_nic', 'slv_date','slv_usage', 'usage.usage_detail']
    column_filters = ['user.mem_nic','slv_date', 'usage.usage_detail']
    column_list = ('user.mem_nic', 'slv_date', 'slv_price','slv_usage', 'usage.usage_detail')
    column_exclude_list = ['slv_usage']
    
    def is_accessible(self):
        
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs) :
        return redirect(url_for('admin/login'))

class mileage_modelView(ModelView) :
    can_delete = False
    can_edit = False
    column_display_all_relations = True
    column_searchable_list = ['user.mem_nic', 'mil_date','mil_usage', 'usage.usage_detail']
    column_filters = ['user.mem_nic','mil_date', 'usage.usage_detail']
    column_list = ('user.mem_nic', 'mil_date', 'mil_price','mil_usage', 'usage.usage_detail')
    column_exclude_list = ['mil_usage']
    
    def is_accessible(self):
        
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs) :
        return redirect(url_for('admin/login'))

class message_modelView(ModelView) :
    can_delete = False
    can_edit = False
    column_display_all_relations = True
    # column_searchable_list = ['user.mem_nic', 'mil_date','mil_usage', 'usage.usage_detail']
    # column_filters = ['user.mem_nic','mil_date', 'usage.usage_detail']
    column_list = ('sender.mem_nic','receiver.mem_nic', 'mess_text', 'mess_date','mess_readtime')
    # column_exclude_list = ['mil_usage']
    
    def is_accessible(self):
        
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs) :
        return redirect(url_for('admin/login'))

class betting(ModelView) :
    can_delete = False
    can_edit = False
    column_display_all_relations = True
    column_display_pk = True
    # column_searchable_list = ['user.mem_nic', 'mil_date','mil_usage', 'usage.usage_detail']
    # column_filters = ['user.mem_nic','mil_date', 'usage.usage_detail']
    column_list = ('bet_no','user.mem_nic','bet_date', 'bet_gold', 'bedang','result_info.name')
    # column_exclude_list = ['mil_usage']
    
    def is_accessible(self):
        
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs) :
        return redirect(url_for('admin/login'))

class betting_detail(ModelView) :
    can_delete = False
    can_edit = False
    column_display_all_relations = True
    
    column_searchable_list = ['bet_no']
    column_list = ('bet.bet_no','game_class_info.name','game_date', 'home', 'away','result_info.name','standard','betting_info.name','home_score','away_score')
    def is_accessible(self):
        
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs) :
        return redirect(url_for('admin/login'))


class MyAdminIndexView(AdminIndexView) :
    def is_accessible(self) :
        return current_user.is_authenticated

class AnalyticsView(BaseView) :
    @expose('/')
    def index(self):

        if current_user.is_authenticated ==True :
            
            sql = "select sum(mem_gold), sum(mem_silver), sum(mem_mil) from member"
            sql2 = "select sum(bet_gold), sum(if(result=1, bet_gold*bedang, null)), date(bet_result_time) from betting group by date(bet_result_time) order by bet_result_time desc"
            sql3 = "select date(mem_signup_date), count(*) from member_info group by date(mem_signup_date) order by date(mem_signup_date) desc"
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(sql)
            sum_money = cursor.fetchone()
            cursor.execute(sql2)
            betting_gold = cursor.fetchall()
            cursor.execute(sql3)
            signup = cursor.fetchall()
            
            conn.close()
            return self.render('admin_analytics.html',sum_money = sum_money, betting_gold=betting_gold, signup = signup)
        else :
            return '금지'
