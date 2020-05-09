from connection.mysql_login import get_connection
import pymysql

def purchasing_silver_item(user_idx, item_idx) :
    
    sql = '''select mem_silver, y.item_cost
             from member, item_list y
             where mem_no = %s and item_no = %s'''
             
    conn = get_connection()
    cursor = conn.cursor()

    
    cursor.execute(sql, (user_idx, item_idx))
    result = cursor.fetchone()

    user_silver = result[0]
    item_price = result[0]
    
    if user_silver < item_price :
        conn.close()
        return 'NO'
    else :
        sql = '''UPDATE member 
             SET mem_silver = mem_silver - (SELECT item_cost FROM item_list WHERE item_no = %s),
	                          mem_gold = mem_gold + (SELECT bonus_gold FROM item_list WHERE item_no = %s)
             WHERE mem_no = %s'''
        
        cursor.execute(sql, (item_idx, item_idx, user_idx))
        
        sql = '''INSERT INTO silver_report(slv_date, slv_price, slv_usage, mem_no) 
                 VALUES(NOW(), - (SELECT item_cost FROM item_list WHERE item_no = %s), 1, %s)'''
        
        cursor.execute(sql,(item_idx, user_idx))
        
        
        if item_idx != '0' and item_idx != '1' and item_idx != '2' :
            
            sql = '''INSERT INTO inventory(item_name, purchase_time ,mem_no, item_no)
                     VALUES((SELECT item_name FROM item_list WHERE item_no = %s), NOW(), %s, %s)'''

            cursor.execute(sql, (item_idx, user_idx, item_idx))
            
            
            if item_idx == '6' :
                sql = '''INSERT INTO gold_report(gld_date, gld_price, gld_usage, mem_no) 
                    VALUES(NOW(), (SELECT bonus_gold FROM item_list WHERE item_no = %s), 0, %s)'''

                cursor.execute(sql,(item_idx, user_idx))
                
        else :
            sql = '''INSERT INTO gold_report(gld_date, gld_price, gld_usage, mem_no) 
                    VALUES(NOW(), (SELECT bonus_gold FROM item_list WHERE item_no = %s), 0, %s)'''

            cursor.execute(sql,(item_idx, user_idx))

            sql = "update member set mem_icon = %s where mem_no = %s"
            cursor.execute(sql,(item_idx, user_idx))
            
        
        sql = '''select mem_silver, mem_gold from member where mem_no = %s'''
        conn.commit()
        cursor.execute(sql,(user_idx))
        result = cursor.fetchall()
        conn.close()
        return result



def store_item_list(store_idx) :

    sql = '''select item_no, item_name, item_cost, bonus_gold, detail, image_url
             from item_list
             where store_no = %s'''

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql, store_idx)
    result = cursor.fetchall()

    item_list = []

    for row in result :
        temp_dic = {}
        temp_dic['item_idx'] = row[0]
        temp_dic['item_name'] = row[1]
        temp_dic['item_cost'] = row[2]
        temp_dic['bonus_gold'] = row[3]
        temp_dic['detail'] = row[4]
        temp_dic['image_url'] = row[5]

        item_list.append(temp_dic)

    conn.close()
    return item_list

def purchasing_mileage_item(user_idx, item_idx) :
    
    sql = '''select mem_mil, y.item_cost
             from member, item_list y
             where mem_no = %s and item_no = %s'''
             
    conn = get_connection()
    cursor = conn.cursor()

    
    cursor.execute(sql, (user_idx, item_idx))
    result = cursor.fetchone()

    user_mileage = result[0]
    item_price = result[0]

    if user_mileage < item_price :
        conn.close()
        return 'NO'
    else :
        
        sql = '''UPDATE member 
                 SET mem_mil = mem_mil - (SELECT item_cost FROM item_list WHERE item_no = %s),
	             mem_gold = mem_gold + (SELECT bonus_gold FROM item_list WHERE item_no = %s)
                 WHERE mem_no = %s'''
        
        cursor.execute(sql, (item_idx, item_idx, user_idx))
        conn.commit()
        
        sql = '''INSERT INTO inventory(item_name, purchase_time ,mem_no, item_no)
                 VALUES((SELECT item_name FROM item_list WHERE item_no = %s), NOW(), %s, %s)'''
    
        cursor.execute(sql, (item_idx, user_idx, item_idx))
        conn.commit()

        sql = '''INSERT INTO mileage_report(mil_date, mil_price, mil_usage, mem_no)
                 VALUES(NOW(),-(SELECT item_cost FROM item_list WHERE item_no = %s), 3, %s)'''
        
        cursor.execute(sql,(item_idx, user_idx))
        conn.commit()

        sql = '''INSERT INTO gold_report(gld_date, gld_price, gld_usage, mem_no) 
                 VALUES(NOW(), (SELECT bonus_gold FROM item_list WHERE item_no = %s), 0, %s)'''

        cursor.execute(sql,(item_idx, user_idx))
        conn.commit()


        sql = '''select mem_mil, mem_gold from member where mem_no = %s'''

        cursor.execute(sql,(user_idx))
        result = cursor.fetchall()
        conn.close()
        return result