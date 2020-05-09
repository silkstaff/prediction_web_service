from flask import Blueprint, render_template, request, session, redirect, flash
from game_center import game_center_dao
from requests import get
import requests
from datetime import date, timedelta
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

game_blue = Blueprint('game_blue', __name__)
site_main = 'https://api.betsapi.com/v1/bet365/'
token = '?token=36917-ClWL9Y0YM7C1hl&'
token2 = '36917-ClWL9Y0YM7C1hl&' 

@game_blue.context_processor
def inject_today_date():
    return {'today_date': datetime.datetime.now().timestamp()}

@game_blue.route('/game_center_proxy', defaults = {'path':'upcoming', 'param':'sport_id=1'})
@game_blue.route('/game_center_proxy/<path:path>', defaults={'param' : 'sport_id=1'})
@game_blue.route('/game_center_proxy/<path:path>/<param>')
def game_center_proxy(path,param) :
    
    return get(f'{site_main}{path}{token}{param}').content

@game_blue.route('/game_center')
def game_center() :
    upcoming_list = game_center_dao.upcoming()
    html = render_template('game_center/game_center.html', upcoming_list = upcoming_list)
    return html

@game_blue.route('/game_center_betting_list', defaults={'page' : 1})
@game_blue.route('/game_center_betting_list/page=<page>')
def game_center_betting_list(page) :
    user_idx = session['user_idx']
    betting_list = game_center_dao.betting_list(user_idx, page)
    betting_detail_list = game_center_dao.betting_detail_list(user_idx, page)
    page_count, page_min, page_max, prev, next = game_center_dao.get_pagenation_info(page, user_idx)
    betting_cancel_count = game_center_dao.betting_cancel_count(user_idx)

    data_dic = {}
    data_dic['page_count'] = page_count
    data_dic['page_min'] = page_min
    data_dic['page_max'] = page_max
    data_dic['prev'] = prev
    data_dic['next'] = next
    data_dic['now_page'] = int(page)

    html = render_template('game_center/game_center_betting_list.html', betting_list = betting_list, betting_detail_list=betting_detail_list, data_dic=data_dic, betting_cancel_count=betting_cancel_count)
    return html

@game_blue.route('/betting', methods = ['post'])
def betting() :

    user_idx = session['user_idx']
    bet_gold = request.form['bet_gold']
    bedang = request.form['bedang']
    game_date = request.form.getlist('game_date')
    game_class = request.form.getlist('game_class')
    home = request.form.getlist('home_name')
    home_bedang = request.form.getlist('home_bedang')
    away = request.form.getlist('away_name')
    away_bedang = request.form.getlist('away_bedang')
    draw_bedang = request.form.getlist('draw_bedang')
    game_no = request.form.getlist('game_no')
    betting = request.form.getlist('betting')
    standard = request.form.getlist('standard')
    game_bedang = request.form.getlist('game_bedang')

    user_gold = game_center_dao.betting_check(user_idx)

    if user_gold < int(bet_gold) :
        return '2'
    remain_gold = game_center_dao.betting(user_idx, int(bet_gold), bedang, game_date, game_class, home, home_bedang, away, away_bedang, draw_bedang, betting, game_no, standard, game_bedang)
    session['user_gold'] = remain_gold
    
    return 'OK'

@game_blue.route('/betting_cancel', methods = ['post'])
def betting_cancel() :
    user_idx = session['user_idx']
    bet_no = request.form['bet_no']
    
    result = game_center_dao.betting_cancel(user_idx, bet_no)
    
    return result


def betting_result() :
    betting_idx = game_center_dao.betting_idx()
    
    
    for i in set(betting_idx) :
        
        url = 'https://api.betsapi.com/v1/bet365/result?event_id='+str(i)+'&token='
        result = requests.get(url+token2).json()
        
        time = result['results'][0]['time_status']
        sport_id = result['results'][0]['sport_id']

        if time == '3' or time == '6' or time == '9':
            game_result = result['results'][0]['ss']
            
            if sport_id=='91':
                home, away=0,0
                for j in range(1,int(max(result['results'][0]['scores'].keys()))+1) :
                    home += int(result['results'][0]['scores'][str(j)]['home'])
                    away += int(result['results'][0]['scores'][str(j)]['away'])
                
                home_set_score, away_set_score = game_result.split('-') 
                home_score = home
                away_score = away
                home_set_score = int(home_set_score)
                away_set_score = int(away_set_score)
                game_center_dao.game_end(i, home_score, away_score, home_set_score, away_set_score)
    
            else :
                home_set_score, away_set_score = game_result.split('-')
                game_center_dao.game_end(i, int(home_set_score), int(away_set_score), int(home_set_score), int(away_set_score))
            
        elif time == '4' or time == '5':
            game_center_dao.game_cancel(i)
    
    user_idx = game_center_dao.betting_hit()
    return str(user_idx)

def upcoming_update() :
    today = date.today()
    tomorrow = date.today() + timedelta(1)

    today = today.strftime('%Y%m%d')
    tomorrow = tomorrow.strftime('%Y%m%d')

    game_list = []
    league_list = {'1' : ['10041282', '10041110', '10041101', '10041095', '10041809', '10041957', '10041109', '10041315'], '18' :['10041830', '10040498'], '91' : ['10040214', '10041185']}
    
    sport_id_list = ['1', '18', '91']
    for sport in sport_id_list :
        for league in league_list[sport] :

            url = 'https://api.betsapi.com/v1/bet365/upcoming?sport_id='+sport+'&day='+today+'&league_id='+league+'&token='
            result = requests.get(url+token2).json()['results']
            for i in range(len(result)) :
                game_idx = {}
                game_idx['sport_id'] = result[i]['sport_id']
                game_idx['id'] = result[i]['id']
                game_idx['time'] = result[i]['time']
                game_idx['league_id'] = league
                game_idx['home_team'] = result[i]['home']['name'].replace("'", "''")
                game_idx['away_team'] = result[i]['away']['name'].replace("'", "''")

                game_list.append(game_idx)

            url = 'https://api.betsapi.com/v1/bet365/upcoming?sport_id='+sport+'&day='+tomorrow+'&league_id='+league+'&token='
            result = requests.get(url+token2).json()['results']

            for i in range(len(result)) :
                
                
                game_idx = {}
                game_idx['sport_id'] = result[i]['sport_id']
                game_idx['id'] = result[i]['id']
                game_idx['time'] = result[i]['time']
                game_idx['league_id'] = league
                game_idx['home_team'] = result[i]['home']['name'].replace("'", "''")
                game_idx['away_team'] = result[i]['away']['name'].replace("'", "''")

                game_list.append(game_idx)
    
    game_center_dao.upcoming_update(game_list)
    
    return 'OK'

sched = BackgroundScheduler() 
sched.start()
sched.add_job(upcoming_update, 'cron', hour="00", minute="00", second='00', id="upcoming_update")
sched.add_job(betting_result, 'cron', minute="59", id="betting_result")
