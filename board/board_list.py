from flask import Blueprint, render_template, request, session, redirect, flash
from board import board_dao
import os
import time

board_blue = Blueprint('board_blue', __name__)

@board_blue.route('/board_list', defaults={'board_idx' : 1, 'page' : 1})
@board_blue.route('/board_list/board=<board_idx>', defaults={'page' : 1})
@board_blue.route('/board_list/board=<board_idx>/page=<page>')
def board_list(board_idx, page) :

    board_name = board_dao.get_board_name(board_idx)

    data_dic = {}
    data_dic['board_name'] = board_name
    data_dic['board_idx'] = board_idx

    data_list = board_dao.getContentList(int(board_idx), int(page))
    
    page_count, page_min, page_max, prev, next = board_dao.get_pagenation_info(int(board_idx), page)


    data_dic['page_count'] = page_count
    data_dic['page_min'] = page_min
    data_dic['page_max'] = page_max
    data_dic['prev'] = prev
    data_dic['next'] = next
    data_dic['now_page'] = int(page)

    

    if board_idx == '0' :
        path = 'community/free-board/list.html'
    elif board_idx == '1' :
        path = 'community/analysis-board/list.html'
    elif board_idx == '2' :
        path = 'customer-center/notice/list.html'
    elif board_idx == '3' :
        path = 'customer-center/1to1ask/list.html'
    html = render_template(path, data_dic=data_dic, data_list=data_list)
    return html

@board_blue.route('/board_write/board=<board_idx>/page=<page>')
def board_write(board_idx, page) :
    data_dic = {}
    data_dic['board_idx'] = board_idx
    data_dic['page'] = page

    if board_idx == '0' :
        path = 'community/free-board/write.html'
    elif board_idx == '1' :
        path = 'community/analysis-board/write.html'
    elif board_idx == '2' :
        path = 'customer-center/notice/write.html'
    elif board_idx == '3' :
        path = 'customer-center/1to1ask/write.html'

    html = render_template(path, data_dic=data_dic)
    return html

@board_blue.route('/board_read/board=<board_idx>/content=<content_idx>', defaults={'page' : 1})
@board_blue.route('/board_read/board=<board_idx>/content=<content_idx>/page=<page>')
def board_read(board_idx, content_idx, page) :

    data_dic = board_dao.get_content(board_idx,content_idx)
    reply_dic = board_dao.reply_list(content_idx)

    data_dic['page'] = page

    if board_idx == '0' :
        path = 'community/free-board/read.html'
    elif board_idx == '1' :
        path = 'community/analysis-board/read.html'
    elif board_idx == '2' :
        path = 'customer-center/notice/read.html'
    elif board_idx == '3' :
        path = 'customer-center/1to1ask/read.html'

    html = render_template(path, data_dic=data_dic, reply_dic=reply_dic)
    return html

@board_blue.route('/board_modify/board=<board_idx>/content=<content_idx>/page=<page>')
def board_modify(board_idx, content_idx, page) :

    data_dic = board_dao.get_content(board_idx, content_idx)
    data_dic['page'] = page


    if board_idx == '0' :
        path = 'community/free-board/modify.html'
    elif board_idx == '1' :
        path = 'community/analysis-board/modify.html'
    elif board_idx == '2' :
        path = 'customer-center/notice/modify.html'
    elif board_idx == '3' :
        path = 'customer-center/1to1ask/modify.html'

    html = render_template(path, data_dic=data_dic)
    return html

@board_blue.route('/faq')
def FAQ() :

    html = render_template('customer-center/faq/faq.html')
    return html

@board_blue.route('/board_write_pro', methods=['post'])
def board_write_pro() :
        
    board_subject = request.form['board_subject']
    board_content = request.form['board_content']
    writer_idx = session['user_idx']
    board_idx = request.form['board_idx']
    
    if board_idx == '1' : 
        board_cost = request.form['board_cost']
        
    else :
        board_cost = 0
    
    if 'board_image' in request.files :
        board_image = request.files['board_image']
        file_name = str(int(time.time())) + board_image.filename

        a1 = os.getcwd() + '/upload/' + file_name
        board_image.save(a1)

    else :
        file_name = None
    content_idx = board_dao.add_content(board_subject, board_content, writer_idx, board_idx, file_name, board_cost)

    return redirect(f'/board_read/board={board_idx}/content={content_idx}')

@board_blue.route('/delete_content', methods=['post'])
def delete_content() :

    content_idx = request.form['content_idx']
    
    check = board_dao.user_board_check(session['user_idx'], content_idx)

    if check == 'OK' :
        board_dao.delete_content(content_idx)
        return 'OK'
    else :
        return '에러입니다.'

@board_blue.route('/modify_content_pro', methods=['post'])
def modify_content() :
    board_subject = request.form['board_subject']
    board_content = request.form['board_content']
    board_content_idx = request.form['board_content_idx']
    board_idx = request.form['board_idx']
    
    if 'board_image' in request.files :
        board_image = request.files['board_image']
        file_name = str(int(time.time())) + board_image.filename

        a1 = os.getcwd() + '/upload/' + file_name
        board_image.save(a1)

    else :
        file_name = None

    check = board_dao.user_board_check(session['user_idx'], board_content_idx)

    if check == 'OK' :

        board_dao.modify_content(board_content_idx, board_subject, board_content, file_name)

        return redirect(f'/board_read/board={board_idx}/content={board_content_idx}')
    else :
        return '접근 권한이 없습니다.'

@board_blue.route('/add_reply_pro', methods=['post'])
def add_reply_pro() :

    r_text = request.form['r_text']
    mem_no = session['user_idx']
    content_idx = request.form['content_idx']
    
    board_dao.add_reply(r_text, mem_no, content_idx)

    return 'OK'

@board_blue.route('/delete_reply_pro', methods=['post'])
def delete_reply_pro() :
    
    reply_idx = request.form['reply_idx']
    
    check = board_dao.user_reply_check(session['user_idx'], reply_idx)

    if check == 'OK' :
        board_dao.reply_delete(reply_idx)
        return 'OK'

    else :
        return "오류입니다."


@board_blue.route('/purchasing_charge_content_pro', methods = ['get','post'])
def buy_charge_content_pro() :

    user_idx = session['user_idx']
    
    if request.method == 'GET' :
        content_idx = request.args.get('content_idx')

        access = board_dao.check_board_access(user_idx, content_idx)
        return access
    else :
        content_idx = request.form['content_idx']
        
        purchasing_ability = board_dao.purchasing_ability(user_idx, content_idx)
        if purchasing_ability != '3' :
            if purchasing_ability != 'NO' :
                
                remain_gold = board_dao.purchasing_content(purchasing_ability, user_idx, content_idx)
                session['user_gold'] = remain_gold 
                return 'OK'
            else :
                return '2' 
        else : 
            return '3'


