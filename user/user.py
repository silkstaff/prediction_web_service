from user import user_dao
from flask import Blueprint, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

user_blue = Blueprint('user_blue', __name__)

@user_blue.route('/user_login')
def user_login() :
    html = render_template('index.html')
    return html

@user_blue.route('/signup')
def user_join() :
    html = render_template('signup/signup.html')
    return html


@user_blue.route('/find_id')
def user_find_id() :
    html = render_template('find-idpw/find-id/find-id.html')
    return html

@user_blue.route('/find_pw')
def user_find_pw() :
    html = render_template('find-idpw/find-pw/find-pw.html')
    return html


@user_blue.route('/terms/terms_conditions')
def terms_conditions() :
    html = render_template('terms/terms_conditions.html')
    return html

    
@user_blue.route('/terms/use_person_info')
def use_person_info() :
    html = render_template('terms/use_person_info.html')
    return html

@user_blue.route('/terms/operation_policy')
def operation_policy() :
    html = render_template('terms/operation_policy.html')
    return html

@user_blue.route('/terms/marketing')
def marketing() :
    html = render_template('terms/marketing.html')
    return html

@user_blue.route('/user_join_pro', methods=['post']) 
def user_join_pro() :
    user_nic = request.form['user_nicname']
    user_id = request.form['user_id']
    user_pw = request.form['user_pw']
    user_name = request.form['user_name']
    user_phone = request.form['user_phone']
    user_birth = request.form['user_birth']
    user_sex = request.form['user_sex']
    user_mail = request.form['user_mail']
    user_rec = request.form['user_rec']
    user_market = request.form['user_market']
    user_gold = request.form['user_gold']
    
    hash = generate_password_hash(user_pw)

    user_dao.add_user(user_id, hash, user_nic, user_gold)
    user_dao.add_user_info(user_id, user_name, user_phone, user_birth, user_sex, user_mail, user_rec, user_market)


    return 'OK'


@user_blue.route('/check_user_id', methods=['post'])
def check_user_id() :
    user_id = request.form['user_id']
    result = user_dao.check_user_id(user_id)

    return result

@user_blue.route('/check_user_nick', methods=['post'])
def check_user_nick() :
    user_nick = request.form['user_nick']
    result = user_dao.check_user_nick(user_nick)

    return result


@user_blue.route('/check_user_rec', methods=['post'])
def check_user_rec() :
    user_rec = request.form['user_rec']
    result = user_dao.check_user_rec(user_rec)

    return result

@user_blue.route('/user_login_pro', methods=['post'])
def user_login_pro() :
    user_id = request.form['user_id']
    user_pw = request.form['user_pw']
    result = user_dao.check_login(user_id, user_pw)
    user_dao.user_ip(result[0], request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    if result == 'NO' :
        return 'NO'
    else :
        session['login'] = 'YES'
        
        session['user_idx'] = result[0]
        session['user_nickname'] = result[1]
        session['user_gold'] = result[2]
        session['user_silver'] = result[3]
        session['user_mil'] = result[4]
        session['user_icon'] = result[6]
        session['user_message'] = result[7]
        session['admin'] = result[5]
        
        return 'YES'

@user_blue.route('/logout', methods=['get','post'])
def logout() :
    session.clear()

    return redirect('/')

@user_blue.route('/find_id', methods=['post'])
def find_id() :
    mem_name = request.form['user_name']
    mem_phone = request.form['user_phone']
    mem_birth = request.form['user_birth']
    mem_sex =request.form['user_sex']


    find_id = user_dao.check_identity_return_id(mem_name, mem_phone, mem_birth, mem_sex)

    if find_id == 'NO' :
        return 'NO'
    else :
        return find_id

@user_blue.route('/find_pw', methods=['post'])
def find_pw() :
    mem_id = request.form['user_id']
    mem_name = request.form['user_name']
    mem_phone = request.form['user_phone']
    mem_birth = request.form['user_birth']
    mem_sex =request.form['user_sex']
    
    pw = user_dao.check_identity_return_pw(mem_id, mem_name, mem_phone, mem_birth, mem_sex)
    
    if pw == 'NO' :
        return 'NO'
    else :
        return pw
    
@user_blue.route('/change_password', methods = ['post'])
def change_password() :
    password = request.form['password']
    user_idx = session['user_idx']
    
    user_dao.change_password(user_idx, password)

    return 'OK'

@user_blue.route('/user_info_check', methods=['post'])
def user_info_check() :
    user_idx = session['user_idx']
    
    result = user_dao.user_info_check(user_idx)
    
    session['login'] = 'YES'
    session['user_idx'] = result[0]
    session['user_nickname'] = result[1]
    session['user_gold'] = result[2]
    session['user_silver'] = result[3]
    session['user_mil'] = result[4]
    session['user_icon'] = result[6]
    session['user_message'] = result[7]
    session['admin'] = result[5]
    
    return 'YES'

@user_blue.route('/gold_loss_check', methods=['post'])
def gold_loss_check() :
    user_idx = session['user_idx']

    user_gold = user_dao.gold_loss_check(user_idx)
    user_secession = user_dao.user_secession_check(user_idx)
    
    if user_secession != None :
        session.clear()
        if user_secession[0] == 1 :
            session['secession_idx'] = user_idx
        return str(user_secession[0])
    elif user_gold == None :
        user_gold = 0
    if user_gold < -100000000 :
        session.clear()
        return 'NO'
    else :
        return 'OK'

@user_blue.route('/user_secession_pro', methods=['post'])
def user_secession_pro() :
    user_idx = session['user_idx']

    user_dao.user_secession(user_idx)
    session.clear()
    return 'OK'


@user_blue.route('/user_secession_cancel_pro', methods=['post'])
def user_secession_cancel_pro() :
    user_idx = request.form['user_idx']

    user_dao.user_secession_cancel(user_idx)

    return 'OK'

@user_blue.route('/signup_tele')
def signup_tele() :
    html = render_template('signup/signup-telephone.html')
    return html