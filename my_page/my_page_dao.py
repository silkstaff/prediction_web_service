from connection.mysql_login import get_connection
import pymysql

def user_item_list(user_idx) :
    
    sql = '''SELECT RAW.item_no, RAW.item_num, image_url, detail, RAW.item_name
             FROM (SELECT item_no, item_name, count(*) item_num FROM inventory WHERE mem_no = %s GROUP BY item_name) RAW
             LEFT JOIN (SELECT item_no, image_url, detail, item_name FROM item_list) RAW2 ON RAW2.item_no = RAW.item_no'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql,(user_idx))
    result_list = cursor.fetchall()

    item_list = []

    for row in result_list :
        temp_dic = {}
        temp_dic['item_idx'] = row[0]
        temp_dic['item_num'] = row[1]
        temp_dic['image_url'] = row[2]
        temp_dic['detail'] = row[3]
        temp_dic['item_name'] = row[4]


        item_list.append(temp_dic)
    conn.close()
    return item_list

def user_info(user_idx) :

    sql = '''select x.mem_id, x.mem_nic, x.mem_gold, x.mem_silver, x.mem_mil, y.mem_phone, y.mem_name, mem_exp
             from member x, member_info y
             where x.mem_no = y.mem_no and x.mem_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (user_idx))

    result = cursor.fetchall()
    
    user_info = {}
    user_info['user_id'] = result[0][0]
    user_info['user_nickname'] = result[0][1]
    user_info['user_gold'] = result[0][2]
    user_info['user_silver'] = result[0][3]
    user_info['user_mil'] = result[0][4]
    user_info['user_phone'] = result[0][5]
    user_info['user_name'] = result[0][6]
    user_info['user_lev'] = int(result[0][7]/10)

    conn.close()
    return user_info

def usage_history(user_idx, type, page) :

    start = (page -1) * 10

    if type == 0 :
        sql = '''SELECT X.slv_date, Y.usage_detail, X.slv_price FROM silver_report X, silver_detail Y 
                 WHERE X.mem_no = %s AND X.slv_usage = Y.slv_usage ORDER BY X.slv_no DESC LIMIT 10 OFFSET %s'''
    elif type == 1 :
        sql = '''SELECT X.gld_date, Y.usage_detail, X.gld_price FROM gold_report X, gold_detail Y 
                 WHERE X.mem_no = %s AND X.gld_usage = Y.gld_usage ORDER BY X.gld_no DESC LIMIT 10 OFFSET %s'''
    elif type == 2 :
        sql = '''SELECT X.mil_date, Y.usage_detail, X.mil_price FROM mileage_report X, mileage_detail Y 
                 WHERE X.mem_no = %s AND X.mil_usage = Y.mil_usage ORDER BY X.mil_no DESC LIMIT 10 OFFSET %s'''
    elif type == 3 :
        pass

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, (user_idx, start))
    result = cursor.fetchall()


    usage_history = []
    for i in result :
        data_list = {}

        data_list['date'] = i[0]
        data_list['detail'] = i[1]
        data_list['price'] = i[2]

        usage_history.append(data_list)
    conn.close()
    return usage_history


def use_change_nickname(user_idx, change_nickname) :

    sql = '''select inv_no
             from inventory
             where mem_no = %s and item_name = "닉네임 변경권"'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, user_idx)
    result = cursor.fetchone()

    if result == None :
        conn.close()
        return 'NO'
    
    sql ='''DELETE FROM inventory WHERE item_name = "닉네임 변경권" AND mem_no = %s LIMIT 1'''

    cursor.execute(sql, (user_idx))
    
    sql = '''update member set mem_nic = %s where mem_no = %s'''
    
    cursor.execute(sql, (change_nickname, user_idx))
    conn.commit()

    conn.close()
    return change_nickname

def get_pagenation_info(type_idx, page, user_idx) :
    
    if type_idx == 0 :
        sql = '''select count(*)
                from silver_report
                where mem_no = %s'''
    elif type_idx == 1 :
        sql = '''select count(*)
                from gold_report
                where mem_no = %s'''
    elif type_idx == 2 :
        sql = '''select count(*)
                from mileage_report
                where mem_no = %s'''

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


def secession_user_info(user_idx) :
    sql = '''select x.mem_no, x.mem_id, x.mem_nic, y.mem_mail, x.mem_secession, y.mem_signup_date
             from member x, member_info y
             where x.mem_no = y.mem_no and x.mem_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, user_idx)
    result = cursor.fetchone()

    conn.close()
    user_info = {}
    user_info['user_idx'] = result[0]
    user_info['user_id'] = result[1]
    user_info['user_nickname'] = result[2]
    user_info['user_mail'] = result[3]
    user_info['user_secession_date'] = result[4]
    user_info['user_signup_date'] = result[5]

    return user_info

def free_gold(user_idx) :
    sql = '''select mem_gold, mem_free_gold
             from member x
             join(select mem_no, mem_free_gold from mem_daily) a on a.mem_no = x.mem_no
             where x.mem_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, user_idx)
    result = cursor.fetchone()
    if result[0] == 0 :
        if result[1] > 2 :
            sql2 = 'update mem_daily set mem_free_gold = mem_free_gold + 1 where mem_no = %s'

            cursor.execute(sql2, user_idx)

            sql3 = 'update member set mem_gold = mem_gold + 10000 where mem_no = %s'

            cursor.execute(sql3, user_idx)

            sql4 = "INSERT INTO gold_report(gld_date, gld_price, gld_usage, mem_no) VALUES(NOW(), (10000, 5, %s)"
            cursor.execute(sql4, (user_idx))
            
            conn.commit()
            conn.close()
            return 'OK'
        else :
            conn.close()
            return '2'
    else :
        conn.close()
        return '3'

