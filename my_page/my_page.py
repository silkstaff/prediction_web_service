from my_page import my_page_dao
from flask import Blueprint, render_template, request, session, redirect

my_blue = Blueprint('my_page_blue', __name__)

@my_blue.route('/my_inventory')
def my_inventory() :
    item_list = my_page_dao.user_item_list(session['user_idx'])

    html = render_template('/mypage/inventory.html', item_list = item_list)
    return html

@my_blue.route('/my_page')
def my_page() :
    user_info = my_page_dao.user_info(session['user_idx'])
    
    html = render_template('/mypage/info/my_page.html', user_info = user_info)
    return html

@my_blue.route('/usage_history',defaults={'board_idx' : 0, 'page' : 0})
@my_blue.route('/usage_history/type=<type>', defaults={'page' : 1})
@my_blue.route('/usage_history/type=<type>/page=<page>')
def usage_history(type, page) :
    user_idx = session['user_idx']
    usage_history = my_page_dao.usage_history(user_idx, int(type), int(page))
    
    page_count, page_min, page_max, prev, next = my_page_dao.get_pagenation_info(int(type), page, user_idx)
    
    data_dic = {}

    data_dic['page_count'] = page_count
    data_dic['page_min'] = page_min
    data_dic['page_max'] = page_max
    data_dic['prev'] = prev
    data_dic['next'] = next
    data_dic['now_page'] = int(page)
    data_dic['type_idx'] = type
    
    html = render_template('/mypage/usage_history.html', usage_history = usage_history, data_dic = data_dic)
    return html


@my_blue.route('/use_change_nickname', methods=['post'])
def use_change_nickname() :
    user_idx = session['user_idx']
    change_nickname = request.form['change_nickname']
    result = my_page_dao.use_change_nickname(user_idx, change_nickname)

    if result =='NO' :
        return '2'
    else :
        session['user_nickname'] = result
        return 'OK'


@my_blue.route('/my_page_update')
def my_page_update() :
    user_info = my_page_dao.user_info(session['user_idx'])
    
    html = render_template('/mypage/info/change_info.html', user_info = user_info)
    return html

@my_blue.route('/my_page_delete')
def my_page_delete() :
    
    html = render_template('/mypage/info/secession.html')
    return html

@my_blue.route('/my_page_delete_cancel')
def my_page_delete_cancel() :
    user_idx = session['secession_idx']
    user_info = my_page_dao.secession_user_info(user_idx)
    html = render_template('/signup/secession_withdrawal.html', user_info = user_info)
    return html


@my_blue.route('/change_info_telephone')
def change_info_telephone() :
    html = render_template('/mypage/info/change_info_telephone.html')
    return html

@my_blue.route('/free_gold', methods=['post'])
def free_gold() :
    user_idx = session['user_idx']

    result = my_page_dao.free_gold(user_idx)

    return result