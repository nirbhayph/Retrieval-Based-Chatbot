import MySQLdb as db
from random import randint
import time
from six.moves import urllib
from wand.image import Image as x1x
from wand.display import display
import wand
import pysftp
from PIL import Image
import requests
from io import BytesIO
from clarifai import rest
import json
from clarifai.rest import ClarifaiApp
app = ClarifaiApp("eSSlQCgzDDqshi0U2XRTg-6gYh0yTbCg1faYChPp", "1IbRENOi-ABMknyufNFjBIYu-KF43jSOQXX65r64")
from clarifai.rest import Image as ClImage
from time import gmtime, strftime



def connect():
	connection = db.Connection(host="107.180.39.237", port=3306, user="ashish_test", passwd="bingipok", db="keyqual_keyhire")
	return connection.cursor(),connection

def send_message_product_slider(row, n):
        print "URL:"
        print row
	outer_list = []
        title=[]
        price=[]
        if n==2:
           price=["Rs. 300","Rs. 400"]
           title=["Mug White", "Mug White Large"]
        elif n==4:
           price=["Rs. 300","Rs. 400","Rs.600", "Rs. 500"]
           title=["TShirt1", "TShirt2", "TShirt3", "TShirt4"]
	for i in range(n):
		inner_dict = {
			"title": title[i],
                        "subtitle": price[i],
			"image_url": row[i],
			"buttons": [
              {
        "type":"web_url",
        "url":row[i],
        "title":"View Item",
        "webview_height_ratio": "tall"
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
        

def get_image_link(recipient):
        c,d = connect()
        c.execute("select * from links where userid='"+str(recipient)+"' ORDER BY timestamp_ DESC")
	row=c.fetchall()
        return row[0][2]

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

def make_image(bg_link,fg_link,sender,count):
        


    fg_url = fg_link
    bg_url = bg_link

    bg = urllib.request.urlopen(bg_url)
    with x1x(file=bg) as bg_img:
        fg = urllib.request.urlopen(fg_url)
        with x1x(file=fg) as fg_img:
            #fg_img.transparent_color(wand.color.Color('#FFF'))
            fg_img.resize(200,200)

            bg_img.composite(fg_img, left=390, top=300)
        fg.close()
        #display(bg_img)
        filex=str(sender)+'-'+str(count)+'-'+strftime("%Y-%m-%d %H:%M:%S", gmtime())+'-pikachu.jpg'
        bg_img.save(filename=filex)
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        srv = pysftp.Connection(host="109.73.164.163", username="root", password="6kH%oVulTFBe", cnopts=cnopts)
        with srv.cd('/var/www/html/cimpress/images'): 
            srv.put(filex) 
        bg.close()
        return str("http://109.73.164.163/cimpress/images/"+filex)
        #bg_img.save("new_image.jpg")
    
        
def change_product_type(recipient,type_):
    c,d = connect()
    #print "Insert Into `links` (`userid`, `link_to_image`) VALUES ('"+recipient+"', '"+link+"')"
    c.execute("Insert Into `cimpress_prod_type` (`userid`, `type`) VALUES ('"+recipient+"', '"+type_+"')")
    d.commit()

def get_product_type(recipient):
        c,d = connect()
        c.execute("select * from cimpress_prod_type where userid='"+str(recipient)+"' ORDER BY timestamp_ DESC")
	row=c.fetchall()
        return row[0][2]

def get_image_quality(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    k = img.size
    if k[0]>500 and k[1]>500:
        return str("yes")
    else:
        return str("no")
    
    
def clarifAI(urlX):
    model = app.models.get('general-v1.3')
    image = ClImage(url='https://s4.scoopwhoop.com/anj/HS01/697943871.jpg')
    ans=model.predict([image])
    #print(ans)
    xx=list()
    for i in range(0,len(ans['outputs'][0]['data']['concepts']) ):
      xx.append(ans['outputs'][0]['data']['concepts'][i]['name'])
      #xx=ans['outputs'][0]['data']['concepts'][i]
    li = []
    taglines='{"results":[{"man":"Suits, Harvey Specter"},{"army":"Indian"},{"wedding":"Marry"},{"success":"India"}]}'
    taglines=json.loads(taglines)
    for m in taglines["results"]:
        for a,b in m.items():
            if a in xx:
                li.append(b)
    return li


    








      
       
	
