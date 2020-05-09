from connection.mysql_login import get_connection
import pymysql
import datetime

def betting_check(user_idx) :
    sql = "select mem_gold from member where mem_no = %s"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, user_idx)
    result = cursor.fetchone()

    conn.close()

    return result[0]

def betting(user_idx, bet_gold, bedang, game_date, game_class, home, home_bedang, away, away_bedang, draw_bedang, betting, game_no, standard, game_bedang) :
    sql = '''insert into betting(mem_no, bet_date, bet_gold, bedang) 
             values((select mem_no from member where mem_no = %s), NOW(), %s, %s)'''

    sql2 = '''select LAST_INSERT_ID()'''

    
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (user_idx, bet_gold, bedang))
    cursor.execute(sql2)
    result = cursor.fetchone()
    bet_no = result[0]

    sql3 = "insert into betting_detail(bet_no, game_date, game_class, home, home_bedang, away, away_bedang, draw_bedang, betting, result, game_no, standard, betting_bedang) values((select bet_no from betting where bet_no = '"+str(bet_no)+"'), '"+str(game_date[0])+"', '"+str(game_class[0])+"', '"+home[0]+"', '"+str(home_bedang[0])+"', '"+away[0]+"', '"+str(away_bedang[0])+"', '"+str(draw_bedang[0])+"', '"+str(betting[0])+"', 0, '"+str(game_no[0])+"', '"+str(standard[0])+"', '"+str(game_bedang[0])+"')"

    j=1
    for i in game_date[1:] :
        
        sql3 += ", ((select bet_no from betting where bet_no = '"+str(bet_no)+"'), '"+str(i)+"', '"+str(game_class[j])+"', '"+home[j]+"', '"+str(home_bedang[j])+"', '"+away[j]+"', '"+str(away_bedang[j])+"', '"+str(draw_bedang[j])+"', '"+str(betting[j])+"', 0, '"+str(game_no[j])+"', '"+str(standard[j])+"', '"+str(game_bedang[j])+"')"
        j+=1
        
    cursor.execute(sql3)

    sql = '''UPDATE member SET mem_gold = mem_gold + %s WHERE mem_no = %s'''

    cursor.execute(sql, (-bet_gold, user_idx))
    

    sql = '''INSERT INTO gold_report(gld_date, gld_price, gld_usage, mem_no) VALUES(NOW(), %s, 1, %s)'''
    cursor.execute(sql, (-bet_gold, user_idx))
    
    sql = '''SELECT mem_gold FROM member WHERE mem_no = %s'''
    cursor.execute(sql, (user_idx))
    remain_gold = cursor.fetchone()

    conn.commit()
    conn.close()
    
    return remain_gold[0]

def betting_cancel(user_idx, bet_no) :
    sql = '''select mem_bet_cancel
             from mem_daily
             where mem_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, user_idx)
    result = cursor.fetchone()
    
    if result[0] > 2 :
        
        conn.close()
        return '2'
    
    else :
        
        sql = "select x.bet_date, min(y.game_date) from betting x, betting_detail y where x.bet_no = %s and y.bet_no = %s"

        cursor.execute(sql, (bet_no, bet_no))

        result = cursor.fetchone()
        
        bet_time = result[0]
        game_time = result[1]
        
        if (datetime.datetime.today() - bet_time).seconds < 600 :
            if datetime.datetime.now() >= game_time :
                conn.close()
                return '4'

            sql = "update mem_daily set mem_bet_cancel = mem_bet_cancel +1 where mem_no = %s"
            cursor.execute(sql, user_idx)

            sql3 = "update member set mem_gold = mem_gold + (select bet_gold from betting where bet_no = %s) where mem_no = %s"
            cursor.execute(sql3, (bet_no, user_idx))

            sql4 = "INSERT INTO gold_report(gld_date, gld_price, gld_usage, mem_no) VALUES(NOW(), (select bet_gold from betting where bet_no = %s), 4, %s)"
            cursor.execute(sql4, (bet_no, user_idx))
            
            sql2 = "DELETE FROM betting WHERE (bet_no = %s)"
            cursor.execute(sql2, bet_no)

            
            conn.commit()
            conn.close()

            return 'OK'
        else :
            
            conn.close()
            return '3'

def betting_idx() :
    sql = '''select game_no
             from betting_detail
             where result = 0'''
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql)
    result = cursor.fetchall()
    
    data_list = []
    for row in result :
        data_list.append(row[0])
    conn.close()
    return data_list

def game_end(game_idx, home_score, away_score, home_set_score, away_set_score) :
    sql = "update betting_detail set home_score = %s, away_score = %s, home_set_score = %s, away_set_score = %s where game_no = %s"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (home_score, away_score, home_set_score, away_set_score, game_idx))

    sql2 = '''select betting_detail_pk
              from betting_detail
              where game_no = %s'''
    cursor.execute(sql2, (game_idx))
    game_end_idx_list = cursor.fetchall()

    for game_end_idx in game_end_idx_list :
        sql = '''select game_class, betting, standard
                from betting_detail
                where betting_detail_pk = %s'''

        cursor.execute(sql, (game_end_idx[0]))
        result = cursor.fetchall()
        
        if result[0][0] == 0 :
            score = home_set_score - away_set_score
            if result[0][1] == 0 :
                if score > 0 : 
                    sql = "update betting_detail set result = 1 where betting_detail_pk = %s"
                else :
                    sql = "update betting_detail set result = 2 where betting_detail_pk = %s"
            elif result[0][1] == 1 :
                if score == 0 :
                    sql = "update betting_detail set result = 1 where betting_detail_pk = %s"
                else :
                    sql = "update betting_detail set result = 2 where betting_detail_pk = %s"
            else :
                if score < 0 :
                    sql = "update betting_detail set result = 1 where betting_detail_pk = %s"
                else :
                    sql = "update betting_detail set result = 2 where betting_detail_pk = %s"

        elif result[0][0] == 1 :
            score = home_score - away_score + result[0][2]
            if result[0][1] == 0 :
                if score > 0 : 
                    sql = "update betting_detail set result = 1 where betting_detail_pk = %s"
                else :
                    sql = "update betting_detail set result = 2 where betting_detail_pk = %s"
            elif result[0][1] == 1 :
                if score == 0 :
                    sql = "update betting_detail set result = 1 where betting_detail_pk = %s"
                else :
                    sql = "update betting_detail set result = 2 where betting_detail_pk = %s"
            else :
                if score < 0 :
                    sql = "update betting_detail set result = 1 where betting_detail_pk = %s"
                else :
                    sql = "update betting_detail set result = 2 where betting_detail_pk = %s"

        elif result[0][0] == 2 :
            score = home_score + away_score
            if result[0][1] == 0 :
                if score < result[0][2] :
                    sql = "update betting_detail set result = 1 where betting_detail_pk = %s"
                else :
                    sql = "update betting_detail set result = 2 where betting_detail_pk = %s"
            else :
                if score > result[0][2] :
                    sql = "update betting_detail set result = 1 where betting_detail_pk = %s"
                else :
                    sql = "update betting_detail set result = 2 where betting_detail_pk = %s"


        cursor.execute(sql, (game_end_idx))
    conn.commit()
    conn.close()

    return 'OK'

def game_cancel(game_idx) :

    sql3 = "select betting_detail_pk from betting_detail where game_no = %s"

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(sql3, (game_idx))
    result = cursor.fetchall()

    for i in result :

        sql2 = "update betting set bedang = bedang / (select betting_bedang from betting_detail where betting_detail_pk = %s), bet_result_time = NOW() where bet_no = (select bet_no from betting_detail where betting_detail_pk = %s)"
        cursor.execute(sql2, (i[0], i[0]))
        sql = "update betting_detail set result = 3, betting_bedang = 1  where betting_detail_pk = %s"
        cursor.execute(sql, (i[0]))
    
    conn.commit()
    conn.close()

    return 'OK'


def betting_hit() :
    

    sql = '''select a.*
             from betting b
             join (select bet_no, count(if (result = 0, 1, null)), count(if (result = 2, 1, null))
             from betting_detail
             group by bet_no) a on a.bet_no = b.bet_no
             where result=0'''
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql)

    result = cursor.fetchall()
    
    mem_idx = []
    for i in result :
        if i[1] == 0 :
            if i[2] == 0 :
                sql = '''update betting set result = 1, bet_result_time = NOW() where bet_no = %s'''

                cursor.execute(sql, i[0])

                sql = "select mem_no, bet_gold, bedang from betting where bet_no = %s"

                cursor.execute(sql, i[0])

                user_no = cursor.fetchall()

                user_idx = user_no[0][0]
                hit_gold = user_no[0][1] * user_no[0][2]

                sql = "update member_info set mem_exp = mem_exp + %s where mem_no = %s"

                cursor.execute(sql, (user_no[0][1]/10000000, user_idx))

                sql = '''UPDATE member SET mem_gold = mem_gold + %s WHERE mem_no = %s'''

                cursor.execute(sql, (hit_gold, user_idx))
                
                
                sql = '''INSERT INTO gold_report(gld_date, gld_price, gld_usage, mem_no) VALUES(NOW(), %s, 3, %s)'''
                cursor.execute(sql, (hit_gold, user_idx))
                
                mem_idx.append(user_idx)

            else :
                sql = '''update betting set result = 2, bet_result_time = NOW() where bet_no = %s'''

                cursor.execute(sql, i[0])

                
                sql = "select mem_no, bet_gold, bedang from betting where bet_no = %s"

                cursor.execute(sql, i[0])

                user_no = cursor.fetchall()

                user_idx = user_no[0][0]
                hit_gold = user_no[0][1] * user_no[0][2]

                sql = "update member_info set mem_exp = mem_exp + %s where mem_no = %s"

                cursor.execute(sql, (user_no[0][1]/10000000, user_idx))
        
    conn.commit()
    conn.close()
    
    return mem_idx
    
def upcoming() :
    sql = "select game_no, time, sport_id, league_id, home_team, away_team from upcoming"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql)
    result = cursor.fetchall()

    data_list = []
    for row in result :
        data_dic = {}
        data_dic['game_no'] = row[0]
        data_dic['time'] = row[1]
        data_dic['sport_id'] = row[2]
        data_dic['league_id'] = row[3]
        data_dic['home_team'] = row[4]
        data_dic['away_team'] = row[5]

        data_list.append(data_dic)
    conn.close()

    return data_list

def upcoming_update(game_list) :
    
    sql = "insert into upcoming (game_no, time, sport_id, league_id, home_team, away_team) values ("+game_list[0]['id']+", "+game_list[0]['time']+", "+game_list[0]['sport_id']+", "+game_list[0]['league_id']+", '"+game_list[0]['home_team']+"', '"+game_list[0]['away_team']+"')"
    j=1
    for i in game_list[1:] :
        sql += ", ("+i['id']+", "+i['time']+", "+i['sport_id']+", "+i['league_id']+", '"+i['home_team']+"', '"+i['away_team']+"')"
        j+=1

    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("truncate upcoming")
    cursor.execute(sql)
    conn.commit()
    conn.close()
    return 'OK'


def betting_list(user_idx, page) :
    start = (int(page) -1) * 10
    sql = "select bet_no, bet_date, bet_gold, bedang, result from betting where mem_no = %s order by bet_date desc limit 10 offset %s"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (user_idx, start))
    result = cursor.fetchall()

    data_list = []
    for row in result :
        data_dic = {}
        data_dic['bet_no'] = row[0]
        data_dic['bet_date'] = row[1]
        data_dic['bet_gold'] = row[2]
        data_dic['bedang'] = row[3]
        data_dic['result'] = row[4]

        data_list.append(data_dic)
    conn.close()

    return data_list


def betting_detail_list(user_idx, page) :
    start = (int(page) -1) * 10
    sql = '''select game_date, game_class, home, home_bedang, away, away_bedang, draw_bedang, betting, result, standard, betting_bedang, home_score, away_score, bet_no
             from betting_detail
             where bet_no in (
                                SELECT * FROM
                                (
                                    SELECT bet_no
                                    FROM betting
                                    where mem_no = %s 
                                    order by bet_date desc 
                                    limit 10 offset %s
                                ) AS subquery
                            )'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (user_idx, start))
    result = cursor.fetchall()

    data_list = []
    for row in result :
        data_dic = {}
        data_dic['game_date'] = row[0]
        data_dic['game_class'] = row[1]
        data_dic['home_team'] = row[2]
        data_dic['home_bedang'] = row[3]
        data_dic['away_team'] = row[4]
        data_dic['away_bedang'] = row[5]
        data_dic['draw_bedang'] = row[6]
        data_dic['betting'] = row[7]
        data_dic['result'] = row[8]
        data_dic['standard'] = row[9]
        data_dic['betting_bedang'] = row[10]
        data_dic['home_score'] = row[11]
        data_dic['away_score'] = row[12]
        data_dic['bet_no'] = row[13]


        data_list.append(data_dic)
    conn.close()

    return data_list


def get_pagenation_info(page, user_idx) :
    
    sql = '''SELECT count(*) FROM betting
            WHERE mem_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (user_idx))
    result = cursor.fetchone()

    count = result[0]
    
    page_count = count // 10
    if page_count % 10 > 0 :
        page_count += 1


    
    min = ((int(page) - 1) // 10) * 10 + 1
    max = min + 9

    if max > page_count :
        max = page_count

    prev = min - 1
    next = max + 1
    
    conn.close()

    return page_count, min, max, prev, next

def betting_cancel_count(user_idx) :

    sql = "select mem_bet_cancel from mem_daily where mem_no = %s"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, user_idx)
    result = cursor.fetchone()

    conn.close()
    
    cancel_count = 3 - result[0]
    
    return cancel_count