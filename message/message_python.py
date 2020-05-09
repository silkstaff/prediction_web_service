from flask import Blueprint, render_template, request, session, redirect, flash
from message import message_dao


message_blue = Blueprint('message_blue', __name__)

@message_blue.route('/message_list', defaults={'type_idx' : 0, 'page' : 1})
@message_blue.route('/message_list/type=<type_idx>', defaults={'page' : 1})
@message_blue.route('/message_list/type=<type_idx>/page=<page>')
def message_list(type_idx, page) :
    user_idx = session['user_idx']
    page_count, page_min, page_max, prev, next = message_dao.get_pagenation_info(int(type_idx), int(page), user_idx)

    data_dic = {}
    data_dic['page_count'] = page_count
    data_dic['page_min'] = page_min
    data_dic['page_max'] = page_max
    data_dic['prev'] = prev
    data_dic['next'] = next
    data_dic['now_page'] = int(page)
    data_dic['type_idx'] = type_idx

    data_list = message_dao.message_list(int(type_idx), user_idx, int(page))

    html = render_template('message/list.html', data_dic = data_dic, data_list = data_list)
    return html

@message_blue.route('/message_read/type=<type_idx>/message=<message_idx>', defaults={'page' : 1})
@message_blue.route('/message_read/type=<type_idx>/message=<message_idx>/page=<page>')
def message_read(type_idx, message_idx, page) :

    data_dic = message_dao.get_message(message_idx)
    
    data_dic['page'] = page
    data_dic['type_idx'] = type_idx

    html = render_template('message/read.html', data_dic=data_dic)
    return html

@message_blue.route('/message_read_pro', methods=['post'])
def message_read_pro() :
    user_idx = session['user_idx']
    message_idx = request.form['message_idx']
    session['user_message'] = message_dao.message_read_pro(user_idx, message_idx)

    return 'OK'


@message_blue.route('/message_write_origin', methods = ['get','post'])
def message_write_origin() :

    if request.method == 'POST' :
        receiver_nickname = request.form['receiver_nickname']
    
        html = render_template('message/write_origin.html', receiver_nickname = receiver_nickname)
        return html
    else :
        html = render_template('message/write_origin.html')
        return html

@message_blue.route('/message_write_random')
def message_write_random() :
    user_idx = session['user_idx']
    message_item_list = message_dao.message_inventory(user_idx)

        
    html = render_template('message/write_random.html', message_item_list = set(message_item_list))
    return html

@message_blue.route('/random_message_pro', methods=['post'])
def random_message_pro() :
    user_idx = session['user_idx']
    count = request.form['count']
    mess_text = request.form['mess_text']
    item_name = request.form['item_name']
    message_dao.random_message_send_pro(count, mess_text, user_idx, item_name)

    return 'OK'

@message_blue.route('/send_message_pro', methods = ['post'])
def send_message_pro() :
    user_idx = session['user_idx']
    receiver_nickname = request.form['receiver_nickname']
    message_text = request.form['mess_text']
    check_nick = message_dao.check_nick(receiver_nickname)

    if check_nick == 'OK':
        message_dao.send_message_pro(receiver_nickname, user_idx, message_text)

        return 'OK'
    else :
        return 'NO'

@message_blue.route('/delete_message_pro', methods = ['post'])
def delete_message_pro() :
    message_idx = request.form.getlist('message_idx')
    
    message_dao.delete_message_pro(message_idx)

    return 'OK'

@message_blue.route('/delete_send_message_pro', methods = ['post'])
def delete_send_message_pro() :
    message_idx = request.form.getlist('message_idx')
    
    message_dao.delete_send_message_pro(message_idx)

    return 'OK'