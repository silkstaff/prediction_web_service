from connection.mysql_login import get_connection
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash



def add_user(mem_id, mem_pw, mem_nic, gold) :
    sql = '''INSERT INTO member(mem_id, mem_pw, mem_nic, mem_gold)
             VALUES(%s, %s, %s, %s)'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (mem_id, mem_pw, mem_nic, gold))

    conn.commit()
    conn.close()

def add_user_info(mem_id, mem_name, mem_phone, mem_birth, mem_sex, mem_mail, mem_rec, mem_market) :
    sql = '''INSERT INTO member_info(mem_no, mem_name, mem_phone, mem_birth, mem_sex, mem_mail, mem_rec, mem_market, mem_signup_date)
             VALUES((SELECT mem_no FROM member WHERE mem_id = %s),
		     %s, %s, %s, %s, %s, %s, %s, NOW())'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (mem_id, mem_name, mem_phone, mem_birth, mem_sex, mem_mail, mem_rec, mem_market))
    
    sql = '''INSERT INTO mem_daily(mem_no) VALUES ((SELECT mem_no FROM member WHERE mem_id = %s))'''

    cursor.execute(sql, mem_id)
    conn.commit()
    conn.close()

def check_user_id(input_id) :
    sql = '''SELECT mem_id
             FROM member
             WHERE mem_id = %s'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (input_id))
    result = cursor.fetchone()
    conn.close()
    if result == None :
        
        return 'YES'
    else :
        
        return 'NO'

def check_user_nick(input_nick) :
    sql = '''SELECT mem_nic
             FROM member
             WHERE mem_nic = %s'''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (input_nick))
    result = cursor.fetchone()
    conn.close()
        
    if result == None :
        return 'YES'
    else :
        
        return 'NO'

def check_user_rec(input_rec) : 
    sql = '''SELECT mem_no
             FROM member
             WHERE mem_id = %s'''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (input_rec))
    result = cursor.fetchone()
    conn.close()
        
    if result == None :
        return 'NO'
    else :
        
        return 'YES'





def check_login(user_id, user_pw) :
    sql = '''SELECT x.mem_no, x.mem_nic, x.mem_gold, x.mem_silver, x.mem_pw, x.mem_mil, y.mem_login, x.mem_admin, x.mem_icon, cnt
             FROM member x, mem_daily y
             join (select count(*) as cnt, ifnull(receiver_no, (select mem_no from member where mem_id=%s)) as receiver_no from message where receiver_no=(select mem_no from member where mem_id=%s) and mess_hidden=0 and mess_read=0) as z on z.receiver_no = mem_no
             WHERE mem_id = %s'''
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (user_id, user_id, user_id))
    result = cursor.fetchall()
    print(result)
    if result == () :
        conn.close()
        return 'NO'
    else :
        
        login = check_password_hash(result[0][4], user_pw)
        result2 = list(result[0])
        del result2[4]
        del result2[5]
        if login == True :
            if result[0][6] != 0 :
                conn.close()
                return result2
            else :
                sql = '''update mem_daily x, member y
                         set x.mem_login = x.mem_login + 1, y.mem_mil = y.mem_mil + 10
                         where x.mem_no=y.mem_no and x.mem_no = %s'''
                cursor.execute(sql, (result[0][0]))
                
                sql = '''INSERT INTO mileage_report(mil_date, mil_price, mil_usage, mem_no) VALUES(NOW(), 10, 2, %s)'''
                cursor.execute(sql, (result[0][0]))
                conn.commit()

                conn.close()
                
                result2[4] += 10
                return result2
        else :
            conn.close()
            return 'NO'

def check_identity_return_id(mem_name, mem_phone, mem_birth, mem_sex) :
    sql = '''SELECT mem_no
             FROM member_info
             WHERE (mem_name = %s and mem_phone = %s and
		            mem_birth = %s and mem_sex = %s)'''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (mem_name, mem_phone, mem_birth, mem_sex))

    result = cursor.fetchone()

    if result == None :
        conn.close()
        return 'NO'
    else :

        sql = '''SELECT mem_id
                 FROM member
                 WHERE mem_no = %s'''

        cursor.execute(sql, (result[0]))

        result = cursor.fetchone()
   
        find_id = result[0]
        conn.close()
        return find_id


def check_identity_return_pw(mem_id, mem_name, mem_phone, mem_birth, mem_sex) :
    sql = '''SELECT mem_no 
             FROM member_info 
             WHERE ((select mem_no
                     from member
                     where mem_id = %s)=mem_no) and mem_name = %s and mem_phone = %s and mem_birth = %s and mem_sex = %s'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (mem_id, mem_name, mem_phone, mem_birth, mem_sex))

    result = cursor.fetchone()

    if result == None :
        conn.close()
        return 'NO' 
    else :
        import string
        import random

        string_pool = string.ascii_letters + string.digits
        pw = ""
        for __ in range(10) :
            pw += random.choice(string_pool)
        
        
        sql = "UPDATE member SET mem_pw = %s WHERE mem_no = %s"
        hash = generate_password_hash(pw)
        cursor.execute(sql, (hash, result[0]))
        conn.commit()
        conn.close()

        return pw 

def change_password(user_idx, password) :
    sql = "UPDATE member SET mem_pw = %s WHERE mem_no = %s"
    hash = generate_password_hash(password)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (hash, user_idx))
    conn.commit()
    conn.close()

    return 'OK'

def user_info_check(user_idx) :
    
    sql = '''SELECT x.mem_no, x.mem_nic, x.mem_gold, x.mem_silver, x.mem_mil, x.mem_admin, x.mem_icon, cnt
             FROM member x, mem_daily y
             join (select count(*) as cnt, ifnull(receiver_no, %s) as receiver_no from message where receiver_no=%s and mess_hidden=0 and mess_read=0) as z on z.receiver_no = mem_no
             WHERE x.mem_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (user_idx, user_idx, user_idx))
    result = cursor.fetchall()
    
    conn.close()
    
    return result[0]

def gold_loss_check(user_idx) :

    sql = '''select sum(if(result=1, bet_gold, -bet_gold))
             from betting
             where date(bet_result_time) = date(NOW()) and mem_no = %s and result != 3'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, user_idx)
    result = cursor.fetchone()

    conn.close()
    return result[0]

def user_secession(user_idx) :
    sql = "update member set mem_secession = NOW() where mem_no = %s"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, user_idx)
    
    conn.commit()
    conn.close()
    return 'OK'


def user_secession_cancel(user_idx) :
    sql = "update member set mem_secession = NULL where mem_no = %s"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, user_idx)
    
    conn.commit()
    conn.close()
    return 'OK'

def user_secession_check(user_idx) :

    sql = '''select if(day(NOW()) - day(mem_secession)<7, 1, 2)
           from member
           where mem_no = %s and mem_secession is not null'''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, user_idx)
    result = cursor.fetchone()

    conn.close()
    return result

def user_ip(user_idx, ip) :
    if ip == '121.138.72.230' or ip == '39.7.57.143' :
        pass
    else :
        sql = "insert into mem_ip (mem_no, mem_ip, login_date) values ((select mem_no from member where mem_no = %s), %s, NOW())"
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (user_idx, ip))
        conn.commit()
        conn.close()
        
