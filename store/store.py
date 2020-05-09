from store import store_dao
from flask import Blueprint, render_template, request, session, redirect

store_blue = Blueprint('store_blue', __name__)

@store_blue.route('/user_item_list')
def user_item_list() :
    user_idx = session['user_idx']

    item_list = store_dao.user_item_list(user_idx)

    return render_template('/', item_list=item_list)

@store_blue.route('/store/type=<type>')
def stroe(type) :
    item_list = store_dao.store_item_list(type)
    return render_template('/store/store.html', item_list = item_list, store_type = type)

@store_blue.route('/purchasing_item_pro', methods=['post'])
def purchasing_item_pro() :

    user_idx = session['user_idx']
    item_idx = request.form['item_idx']
    store_type = request.form['store_type']
    
    if store_type == '0' :
        
        purchasing_abiliy = store_dao.purchasing_silver_item(user_idx, item_idx)
        
        if purchasing_abiliy == 'NO' :
            return '구매 가능한 은화가 부족합니다.'

        else :
            
            user_silver = purchasing_abiliy[0][0]
            user_gold = purchasing_abiliy[0][1]

            session['user_silver'] = user_silver
            session['user_gold'] = user_gold

            return redirect('/store/type=0')

    elif store_type == '1' :
        purchasing_abiliy = store_dao.purchasing_mileage_item(user_idx, item_idx)

        if purchasing_abiliy == 'NO' :
            return '구매 가능한 마일리지가 부족합니다.'

        else :
            
            user_silver = purchasing_abiliy[0][0]
            user_gold = purchasing_abiliy[0][1]
            if item_idx == 0 or item_idx == 1 or item_idx == 2 :
                session['user_icon'] = item_idx
            session['user_mil'] = user_silver
            session['user_gold'] = user_gold

            return redirect('/store/type=1')