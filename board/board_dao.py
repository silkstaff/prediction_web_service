from connection.mysql_login import get_connection
import pymysql
from flask import session, request

def get_board_name(board_idx) :
    
    sql = '''select b_title from board where b_no=%s'''
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (board_idx))
    
    result = cursor.fetchone()
    board_name = result

    conn.close()
    return board_name


def add_content(content_subject, content_text, content_writer_idx, content_board_idx, file_name, content_cost) :
    
    sql = '''INSERT INTO board (b_class, b_title, b_text, b_cost, b_date, mem_no)
             VALUES(%s, %s, %s, %s, NOW(), %s)'''
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (content_board_idx, content_subject, content_text, content_cost, content_writer_idx))    
    
    sql = '''select mem_board
             from mem_daily
             where mem_no = %s'''

    cursor.execute(sql, (content_writer_idx))
    result = cursor.fetchone()
    
    if result[0] < 5 and content_board_idx != 3:
        sql = '''UPDATE mem_daily x, member y SET x.mem_board = x.mem_board + 1, y.mem_mil = y.mem_mil + 5 WHERE x.mem_no = %s and y.mem_no = %s'''

        cursor.execute(sql, (content_writer_idx,content_writer_idx))
        
        sql = '''INSERT INTO mileage_report(mil_date, mil_price, mil_usage, mem_no) VALUES(NOW(), 5, 0, %s)'''

        cursor.execute(sql, content_writer_idx)
        session['user_mil'] += 5
    
    sql2 = '''select max(b_no)
              from board
              where b_hidden=0''' 
    cursor.execute(sql2)
    result2 = cursor.fetchone()
    content_idx = result2[0]
    conn.commit()
        
    conn.close()
    
    return content_idx


def get_content(board_idx, content_idx) :
    
    sql = '''SELECT b_class, b_title, b_text, mem_nic, b_date, x.mem_no, b_cost
             FROM board x, member y
             WHERE x.mem_no = y.mem_no and x.b_no = %s and x.b_class = %s'''
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (content_idx, board_idx))
    
    result = cursor.fetchone()
    data_dic = {}
    data_dic['user_name'] = result[3]
    data_dic['content_subject'] = result[1]
    data_dic['content_text'] = result[2]
    data_dic['content_file'] = None 
    data_dic['content_idx'] = content_idx
    data_dic['content_board_idx'] = result[0]
    data_dic['content_writer_idx'] = result[5]
    data_dic['content_date'] = result[4]
    data_dic['board_cost'] = result[6]

    conn.close()

    return data_dic


def getContentList(board_idx, page) :

    
    start = (page -1) * 10

    conn = get_connection()
    cursor = conn.cursor()
        

    if board_idx == 0 :
        sql = '''SELECT RAW.b_no, b_date, b_title, r_num, mem_nic, b_view
                 FROM (SELECT B.b_no, B.b_class, B.b_date, B.b_title, M.mem_nic, B.b_view 
	                   FROM board B, member M 
	                   WHERE B.b_class = 0 AND B.mem_no = M.mem_no AND b_hidden=0) RAW
                 LEFT JOIN (SELECT R.b_no, count(*) r_num FROM reply R WHERE r_hidden = 0 GROUP BY R.b_no) A on A.b_no = RAW.b_no
                 ORDER BY RAW.b_no DESC     LIMIT 10 OFFSET %s'''

        cursor.execute(sql, (start))

        result_list = cursor.fetchall()

        data_list = []

        for row in result_list :
            temp_dic = {}
            temp_dic['content_idx'] = row[0]
            temp_dic['content_subject'] = row[2]
            temp_dic['content_writer_name'] = row[4]
            temp_dic['content_date'] = row[1]
            temp_dic['view'] = row[5]
            temp_dic['board_idx'] = board_idx
            temp_dic['reply_count'] = row[3]

            data_list.append(temp_dic)

    elif board_idx == 1 :
        sql = '''SELECT RAW.b_no, b_date, b_title, b_cost, r_num, mem_nic, b_view
                 FROM (SELECT B.b_no, B.b_class, B.b_date, B.b_cost, B.b_title, M.mem_nic, B.b_view
	                   FROM board B, member M 
	             WHERE B.b_class = 1 AND B.mem_no = M.mem_no AND b_hidden=0) RAW 
                 LEFT JOIN (SELECT R.b_no, count(*) r_num FROM reply R WHERE r_hidden = 0 GROUP BY R.b_no) A on A.b_no = RAW.b_no
                 ORDER BY RAW.b_no DESC LIMIT 10 OFFSET %s'''
        
        cursor.execute(sql, (start))

        result_list = cursor.fetchall()

        data_list = []

        for row in result_list :
            temp_dic = {}
            temp_dic['content_idx'] = row[0]
            temp_dic['content_subject'] = row[2]
            temp_dic['content_writer_name'] = row[5]
            temp_dic['content_date'] = row[1]
            temp_dic['view'] = row[6]
            temp_dic['board_idx'] = board_idx
            temp_dic['board_cost'] = row[3]
            temp_dic['reply_count'] = row[4]

            data_list.append(temp_dic)
    
    elif board_idx == 2 :
        sql = '''SELECT b_no, b_date, b_title, mem_nic, b_view  
                 FROM board B, member M
                 WHERE b_class = 2 AND B.mem_no = M.mem_no AND b_hidden=0
                 ORDER BY b_no DESC
                 LIMIT 10 OFFSET %s'''

        cursor.execute(sql, (start))

        result_list = cursor.fetchall()

        data_list = []

        for row in result_list :
            temp_dic = {}
            temp_dic['content_idx'] = row[0]
            temp_dic['content_subject'] = row[2]
            temp_dic['content_writer_name'] = row[3]
            temp_dic['content_date'] = row[1]
            temp_dic['view'] = row[4]
            temp_dic['board_idx'] = board_idx
            
            data_list.append(temp_dic)
    
    elif board_idx == 3 :

        if session['admin'] == 1 :
            sql = '''SELECT RAW.b_no, b_date, b_title, r_num, mem_nic
                     FROM (SELECT B.b_no, B.b_class, B.b_date, B.b_title, M.mem_nic, B.b_view
                           FROM board B, member M
                           WHERE b_class = 3 AND B.mem_no = M.mem_no AND b_hidden = 0) RAW # b_class = 3: 일대일문의게시판 분류 번호임
                     LEFT JOIN (SELECT R.b_no, count(*) r_num FROM reply R WHERE r_hidden = 0 GROUP BY R.b_no) A on A.b_no = RAW.b_no
                     ORDER BY RAW.b_no DESC LIMIT 10 OFFSET %s'''
                
            cursor.execute(sql, (start))

        else :
            sql = '''SELECT RAW.b_no, RAW.b_date, RAW.b_title, r_num, RAW.mem_nic
                     FROM (SELECT B.b_no, B.b_date, B.b_class, B.b_title, B.b_text, M.mem_no, M.mem_nic FROM board B, member M WHERE B.mem_no = %s AND b_class = 3 AND b_hidden = 0) RAW
                     LEFT JOIN (SELECT R.b_no, count(*) r_num FROM reply R WHERE r_hidden = 0 GROUP BY R.b_no) A on A.b_no = RAW.b_no
                     WHERE mem_no = %s
                     ORDER BY RAW.b_no DESC LIMIT 10 OFFSET %s'''

            cursor.execute(sql,(session['user_idx'], session['user_idx'], start))
        
        result_list = cursor.fetchall()

        data_list = []

        for row in result_list :
            temp_dic = {}
            temp_dic['content_idx'] = row[0]
            temp_dic['content_subject'] = row[2]
            temp_dic['content_writer_name'] = row[4]
            temp_dic['content_date'] = row[1]
            temp_dic['board_idx'] = board_idx
            temp_dic['reply_count'] = row[3]

            data_list.append(temp_dic)

    

    conn.close()

    return data_list


def get_pagenation_info(board_idx, page) :
    
    
    if board_idx == 3 and session['admin'] != 1 :
        
        sql = '''SELECT count(*) FROM board 
             WHERE b_class = %s and b_hidden = 0 and mem_no = %s'''

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (board_idx, session['user_idx']))
        result = cursor.fetchone()
    
    else :
        
        sql = '''SELECT count(*) FROM board 
             WHERE b_class = %s and b_hidden = 0'''

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (board_idx))
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


def delete_content(content_idx) :

    sql = '''UPDATE board SET b_hidden = 1 WHERE b_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (content_idx))

    conn.commit()
    conn.close()


def modify_content(content_idx, content_subject, content_text, file_name) :

    sql = '''UPDATE board 
             SET b_title = %s, b_text = %s'''

    if file_name != None :
        sql += ', content_file= %s'

    sql += 'where b_no= %s'

    conn = get_connection()

    cursor = conn.cursor()

    if file_name != None :
        cursor.execute(sql, (content_subject, content_text, file_name, content_idx))
    else :
        cursor.execute(sql, (content_subject, content_text, content_idx))

    conn.commit()
    conn.close()



def add_reply(r_text, mem_no, b_no) :
    sql = '''INSERT INTO reply(r_text, r_date, mem_no, b_no)
             VALUES (%s, now(),%s, %s)'''


    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(sql, (r_text, mem_no, b_no))
    
    sql = '''select mem_reply
             from mem_daily
             where mem_no = %s'''

    
    cursor.execute(sql, (mem_no))
    result = cursor.fetchone()

    if result[0] < 5 :
        sql = '''UPDATE mem_daily x, member y SET x.mem_reply = x.mem_reply + 1, y.mem_mil = y.mem_mil + 2 WHERE x.mem_no = %s and y.mem_no = %s'''

        cursor.execute(sql, (mem_no,mem_no))
        
        sql = '''INSERT INTO mileage_report(mil_date, mil_price, mil_usage, mem_no) VALUES(NOW(), 2, 1, %s)'''

        cursor.execute(sql, mem_no)
        session['user_mil'] += 2
    
    conn.commit()    
    conn.close()

def reply_delete(r_no) :
    sql = '''UPDATE reply SET r_hidden = 1 WHERE (r_no = %s)'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (r_no))
    
    conn.commit()
    conn.close()

def reply_list(content_idx) :
    sql = '''select x.r_text, x.r_date, y.mem_nic, y.mem_no, x.r_no, y.mem_icon
             from reply x, member y
             where x.r_hidden = 0 and x.b_no = %s and x.mem_no = y.mem_no'''
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (content_idx))
    result_list = cursor.fetchall()
    
    conn.close()

    data_list = []

    for row in result_list :
        temp_dic = {}
        temp_dic['reply_text'] = row[0]
        temp_dic['reply_date'] = row[1]
        temp_dic['reply_nickname'] = row[2]
        temp_dic['reply_writer_idx'] = row[3]
        temp_dic['reply_idx'] = row[4]
        temp_dic['user_icon'] = row[5]
        
        data_list.append(temp_dic)

    

    
    return data_list

def user_board_check(user_idx, content_idx) :
    sql = '''select mem_no
             from board
             where b_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql,(content_idx))
    result = cursor.fetchone()

    if result[0] == user_idx :
        
        conn.close()
        return 'OK'
    else :
        
        conn.close()
        return 'NO'

def user_reply_check(user_idx, reply_idx) :
    sql = '''select mem_no
             from reply
             where r_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql,(reply_idx))
    result = cursor.fetchone()

    if result[0] == user_idx :
        
        conn.close()
        return 'OK'
    else :
        
        conn.close()
        return 'NO'

def purchasing_ability(user_idx, content_idx) :
    sql = '''SELECT x.mem_gold, y.b_cost FROM member x, board y WHERE x.mem_no = %s and y.b_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (user_idx, content_idx))
    result = cursor.fetchall()

    sql2 = '''select mem_exp
             from member_info
             where mem_no = %s'''

    cursor.execute(sql2, (user_idx))
    result2 = cursor.fetchone()
    
    conn.close()
    user_gold = result[0][0]
    content_cost = result[0][1]
    
    if result2[0] >= 50 :
        if user_gold >= content_cost :
            
            return content_cost
        else :
            
            return 'NO'
    else :
        
        return '3'

    

def purchasing_content(board_cost, user_idx, content_idx) :
    sql = '''UPDATE member SET mem_gold = mem_gold + %s WHERE mem_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (int(-board_cost), user_idx))
    
    
    sql = '''INSERT INTO gold_report(gld_date, gld_price, gld_usage, mem_no) VALUES(NOW(), %s, 2, %s)'''
    cursor.execute(sql, (int(-board_cost), user_idx))
    
    
    sql = '''INSERT INTO board_access(b_no, mem_no) VALUES (%s, %s)'''
    cursor.execute(sql, (content_idx, user_idx))
    
    
    sql = '''SELECT mem_gold FROM member WHERE mem_no = %s'''
    cursor.execute(sql, (user_idx))
    remain_gold = cursor.fetchone()

    sql = '''UPDATE member M  SET mem_gold = mem_gold + (SELECT b_cost FROM board WHERE b_no = %s) 
             WHERE M.mem_no = (SELECT B.mem_no FROM board B WHERE b_no = %s)'''
    cursor.execute(sql, (content_idx, content_idx))
    
    
    sql = '''INSERT INTO gold_report(gld_date, gld_price, gld_usage, mem_no) 
             VALUES(NOW(), (SELECT b_cost FROM board WHERE b_no = %s), 2, (SELECT mem_no FROM board WHERE b_no = %s))'''
    cursor.execute(sql, (content_idx, content_idx))
    conn.commit()

    conn.close()
    return remain_gold[0]

def check_board_access(user_idx, content_idx) :
    sql = '''SELECT mem_no FROM board_access WHERE b_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (content_idx))
    result = cursor.fetchall()

    conn.close()
    for i in result :
        if user_idx in i :
            return 'OK'
    
    return 'NO'