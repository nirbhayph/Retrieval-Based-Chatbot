import MySQLdb as db
from random import randint
import time
def connect():
	connection = db.Connection(host="107.180.39.237", port=3306, user="ashish_test", passwd="bingipok", db="keyqual_keyhire")
	return connection.cursor(),connection
#we get the row variable which contains the data of all rows and the n variable which contains the number of rows
def get_RESULT_slider(row, n, MYSQL_COL_NUM_1, MYSQL_COL_NUM_2):
	outer_list = []
	for i in range(n):
		inner_dict = {
			"title": row[i][MYSQL_COL_NUM_1],
                        "subtitle": row[i][MYSQL_COL_NUM_2],
			"image_url": "http://109.73.164.163/FLEXI_PORT/flexi_port.png",
			"buttons": [{
				"type": "web_url",
				"url": "https://www.theflexiport.com",
				"title": "View"
			}, {
				"type": "web_url",
				"url": "https://www.theflexiport.com",
				"title": "Apply"
			}, 
                               {
				"type": "element_share"
				
             }]
		}
		outer_list.append(inner_dict)
	return outer_list

# ASSEMSSMENT SLIDER TEMPLATE BEGINS HERE #

def get_quick_replies(row, n, NOTER):
        outer_list=[]
        for i in range(n):
	  inner_dict = {
				"content_type":"text",
                                "title":str(row[i][1]),
                                "payload":str(row[i][0])+"--NX--"+NOTER
	  }
          outer_list.append(inner_dict)	
	return outer_list

def get_quick_replies_sub(row, item_no):
          outer_list=[]
	  inner_dict = {
				"type":"postback",
                                "title":"Select",
                                "payload":str(row[item_no][0])+"--XA--"+str(row[item_no][1])+"--XA--"+str(row[item_no][2])
	  }
          outer_list.append(inner_dict)	
	  return outer_list



def get_main_cat():
	c = connect()
	c.execute("SELECT * FROM zz_category")
	row=c.fetchall()
        print "Category Count is "+str(len(row))
	return row, len(row)

def get_sub_cat(cat_id):
	c = connect()
	c.execute("SELECT * FROM zz_subcategory where category_id='"+str(cat_id)+"'")
	row=c.fetchall()
        print "Subcategory Count is "+str(len(row))
	return row, len(row)

def store_image_link(recipient,link):
        c,d = connect()
        c.execute("SELECT * FROM links")
	row=c.fetchall()
        print row
        print "Insert Into `links` (`userid`, `link_to_image`) VALUES ('"+recipient+"', '"+link+"')"
        c.execute("Insert Into `links` (`userid`, `link_to_image`) VALUES ('"+recipient+"', '"+link+"')")
        d.commit()
        

def get_last_filter(recipient):
        c = connect()
        c.execute("select * from zz_last_search_filter where recipient='"+str(recipient)+"'")
	row=c.fetchall()
        return row, len(row)

def get_FINAL_result(CAT, SUB_CAT): 
        c = connect()
        c.execute("select * from zz_work_posts where category_id='"+str(CAT)+"' and skill_id='"+str(SUB_CAT)+"' LIMIT 10")
	row=c.fetchall()
        return row, len(row)

def get_the_services(CAT):
        c = connect()
        c.execute("select * from zz_services where category_id='"+str(CAT)+"' LIMIT 10")
	row=c.fetchall()
        return row, len(row)
        









      
       
	
