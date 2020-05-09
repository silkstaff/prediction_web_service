from connection.mysql_login import get_connection
import pymysql
import random

def get_pagenation_info(type_idx, page, user_idx) :
    
    
    if type_idx == 0 :
        
        sql = '''SELECT count(*) mess_num
                 FROM message
                 WHERE receiver_no = %s and mess_hidden = 0'''
    else :
        sql = '''SELECT count(*) mess_num
                 FROM message
                 WHERE sender_no = %s and mess_send_hidden = 0'''
    
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

def message_list(type_idx, user_idx, page) :
    if type_idx == 0 :
        sql = '''SELECT MES.mess_no, MES.mess_text, MES.mess_read, MES.mess_date, MEM.mem_nic sender_nic
                 FROM message MES, member MEM
                 WHERE receiver_no = %s AND MEM.mem_no = sender_no and mess_hidden = 0
                 ORDER BY mess_no DESC LIMIT 10 OFFSET %s'''
    else :
        sql = '''SELECT MES.mess_no, MES.mess_text, MES.mess_read, MES.mess_date, MEM.mem_nic receiver_nic
                 FROM message MES, member MEM
                 WHERE sender_no = %s AND MEM.mem_no = receiver_no and mess_send_hidden = 0
                 ORDER BY mess_no DESC LIMIT 10 OFFSET %s'''
    
    conn = get_connection()
    cursor = conn.cursor()

    start = (page -1) * 10


    cursor.execute(sql, (user_idx,start))
    result_list = cursor.fetchall()
    
    conn.close()

    data_list = []

    for row in result_list :
        temp_dic = {}
        temp_dic['message_idx'] = row[0]
        temp_dic['message_text'] = row[1]
        temp_dic['message_read'] = row[2]
        temp_dic['message_date'] = row[3]
        temp_dic['message_receiver_nic'] = row[4]
        
        data_list.append(temp_dic)

    
    return data_list

def get_message(message_idx) :
    
    sql = '''SELECT mess_text, mess_date, M.mem_nic sender_nic, mess_read, mess_no
             FROM message, member M 
             WHERE mess_no = %s AND M.mem_no = message.sender_no'''
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (message_idx))
    
    result = cursor.fetchone()
    data_dic = {}
    data_dic['message_text'] = result[0]
    data_dic['message_date'] = result[1]
    data_dic['sender_nic'] = result[2] 
    data_dic['message_read'] = result[3]
    data_dic['message_idx'] = result[4]
    
    conn.close()

    return data_dic

def delete_message_pro(message_idx) :

    if len(message_idx)>1 :
        sql = "update message set mess_hidden = 1 where mess_no in " + str(tuple(message_idx))
    else :
        sql = "update message set mess_hidden = 1 where mess_no in (" + str(message_idx[0])+')'
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)

    conn.commit()
    conn.close()
    return 'OK'


def delete_send_message_pro(message_idx) :

    if len(message_idx)>1 :
        sql = "update message set mess_send_hidden = 1 where mess_no in " + str(tuple(message_idx))
    else :
        sql = "update message set mess_send_hidden = 1 where mess_no in (" + str(message_idx[0])+')'
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)

    conn.commit()
    conn.close()
    return 'OK'

def message_read_pro(user_idx, message_idx) :

    sql = '''UPDATE member SET mem_mes = (SELECT count(*) FROM message WHERE receiver_no = %s) 
    WHERE mem_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (user_idx, user_idx))

    sql = '''UPDATE message SET mess_read = 1, mess_readtime = NOW() WHERE mess_no = %s'''
    cursor.execute(sql, (message_idx))
    conn.commit()

    sql2 = '''select count(*)
              from message
              where receiver_no = %s and mess_hidden=0 and mess_read = 0'''
    
    cursor.execute(sql2, (user_idx))
    message = cursor.fetchone()

    
    conn.close()
    
    return message[0]

def random_message_send_pro(count, mess_text, sender_no, item_name) :

    conn = get_connection()
    cursor = conn.cursor()
    count = int(count)
    sql = '''select mem_no from member order by rand() limit %s'''

    cursor.execute(sql, count)
    row = cursor.fetchall()
    
    sql = '''DELETE FROM inventory WHERE item_name = %s AND mem_no = %s LIMIT 1'''

    cursor.execute(sql, (item_name, sender_no))
    sql = "insert into message(mess_text, mess_date, sender_no, receiver_no) VALUES('"+str(mess_text)+"', NOW(), "+str(sender_no)+", "+str(row[0][0])+")"

    for i in row[1:] :
        sql += ", ('"+str(mess_text)+"', NOW(), "+str(sender_no)+", "+str(i[0])+")"

    cursor.execute(sql)
    conn.commit()

    conn.close()

    return 'OK'

def send_message_pro(receiver_nickname, sender_no, mess_text) :

    sql = '''insert into message(mess_text, mess_date, sender_no, receiver_no) values(%s, NOW(), %s, (select mem_no
                                                                                                      from member
                                                                                                      where mem_nic = %s))'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (mess_text, sender_no, receiver_nickname))
    conn.commit()

    conn.close()

    return 'OK'

def check_nick(receiver_nickname) :

    sql = '''select x.mem_no, mem_secession
             from member x
             where x.mem_nic = %s and mem_secession is null'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, receiver_nickname)
    result = cursor.fetchone()
    conn.close()
    if result != None :
        return 'OK'
    else :
        return 'NO'

def message_inventory(user_idx) :
    
    sql = '''select item_no, item_name
             from inventory
             where mem_no = %s and item_no in (3,4,5)'''
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, user_idx)
    message_list = cursor.fetchall()

    conn.close()

    return message_list