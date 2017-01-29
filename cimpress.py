from flask import Flask, request
import json
import requests
from methods import *
from six.moves import urllib
from wand.image import Image as x2x
from wand.display import display
import wand
import pysftp


app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAAalhZC68jJABAGGz2RF9HslYsd4RduDnjZAImzjILEVsV8dDpsq82Wr5pUjdTm8L0mYYtPnnewyuaq6w4RAZAAfWNjolhTKChTqZCCu9B7MhRuNuugIyAYOgzJkNuZCLynM88c143mlhJVZAIihZAqlbif4hHLmZBZA9tXX4f9q02gZDZD'

@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification."
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    print "Verification failed!"
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print "Handling Messages"
  #PAYLOAD SECTION HANDLING
  image_url=""
  datax = request.get_json()
  if datax["object"] == "page":
    
    for entry in datax["entry"]:
      for messaging_event in entry["messaging"]:
        sender = str(messaging_event["sender"]["id"].encode('unicode_escape'))  
 
        if messaging_event.get("postback"):
          print "Postback"
          print str(messaging_event["postback"]["payload"].encode('unicode_escape'))
          if str(messaging_event["postback"]["payload"].encode('unicode_escape'))=="SHOW_OPTIONS":
            bg_links=""
            P_TYPE = get_product_type(sender)
            mugs=["http://omnihousewareinc.com/wp-content/uploads/2014/02/White_11oz_mug.jpg","https://files.giftsoffer.ru/reviewer/thumbnails/www/4663_8_psd_1000x1000.jpg"]
            shirts=['https://blueinc_co_uk.secure-cdn.visualsoft.co.uk/images/mens-black-line-up-girl-t-shirt-p20285-22116_zoom.jpg', "http://images.junostatic.com/full/IS355782-01-01-BIG.jpg", "https://www.wordans.com/wvc-1440801044/wordansfiles/model_specifications/2015/8/28/116313/116313_original.jpg", "https://is.alicdn.com/img/pb/384/390/383/383390384_036.jpg"]
            xr=""
            if P_TYPE=="MG":
                 xr="mugs"
                 bg_links=mugs
            elif P_TYPE=="CL":
                 xr="clo"
                 bg_links=shirts
            list_f=[]
            fg_link = get_image_link(sender)
            count=0
            for i in bg_links:
                list_f.append(make_image(i,fg_link,sender,count,xr))
                count=count+1
            print list_f
            product_slider(PAT,sender,list_f)
          elif str(messaging_event["postback"]["payload"].encode('unicode_escape'))=="VC":
            send_message_VC(PAT, sender) 
            change_product_type(sender,"VC")
          elif str(messaging_event["postback"]["payload"].encode('unicode_escape'))=="MG":
            send_message(PAT, sender,"Please upload an image you wish to add on the Mug") 
            change_product_type(sender,"MG")
          elif str(messaging_event["postback"]["payload"].encode('unicode_escape'))=="CL":
            send_message(PAT, sender,"Please upload an image you wish to use")
            change_product_type(sender,"CL")
          elif str(messaging_event["postback"]["payload"].encode('unicode_escape'))=="YES_VC":
            send_message(PAT, sender,"Please upload your logo image")
            change_product_type(sender,"VC")
          elif str(messaging_event["postback"]["payload"].encode('unicode_escape'))=="NO_VC":
            send_message_redirect_cimpress(PAT, sender) 
          elif str(messaging_event["postback"]["payload"].encode('unicode_escape'))=="BUY_PROD":
            share_location(PAT, sender) 
            set_box(sender,"LOC")   
 
        if messaging_event.get("message"):
          
          for item,value in messaging_event["message"].iteritems():
          
            if(str(item)=="attachments"):
                print item
                if check_box(sender)=="LOC":
                      send_message(PAT,sender,"Thank you for placing an order with Vista Print")
                      get_contact_details(PAT,sender)
                      set_box(sender,"NOT_LOC")
                      break
                for mem,aea in value[0].iteritems(): 
                   if(mem=="payload"):
                      image_url=str(aea["url"])
                      print image_url
                      #Check for image quality
                      IMAGE_QUALITY=get_image_quality(image_url)
                      if IMAGE_QUALITY=="yes":
                          nnx = urllib.request.urlopen(image_url)
                          with x2x(file=nnx) as IMAG:
                              filex=str(sender)+'-IMAG.jpg'
                              IMAG.save(filename=filex)
                          send_message(PAT, sender,"Congratualtions! Your image cleared the quality test")
                          store_image_link(sender,image_url)
                          #CALL Vision API
                          PROD_TYPE = get_product_type(sender)
                          if PROD_TYPE=="MG" or PROD_TYPE=="CL":
                              m = clarifAI(image_url)
                              if len(m)>0:
                                  send_message(PAT,sender,"We have some taglines you can use based on your image ;)")
                              for i in range(0,len(m)):
                                  send_message(PAT,sender,str(m[i].encode('unicode_escape')))
                              send_message_edit(PAT,sender)
                          elif PROD_TYPE=="VC":
                              cnopts = pysftp.CnOpts()
        		      cnopts.hostkeys = None
                              srv = pysftp.Connection(host="109.73.164.163", username="root", password="6kH%oVulTFBe", cnopts=cnopts)
                              with srv.cd('/var/www/html/cimpress/images'): 
                                  srv.put(filex)
                              r = requests.get("http://109.73.164.163/cimpress/images/g-cloud.php?filex="+filex+"&sender="+sender)
                              if len(str(r.content))>0:
                                  send_message(PAT,sender,"Seems like you work in "+str(r.content))
                              send_message_redirect_cimpress(PAT, sender)    
                      elif IMAGE_QUALITY=="no":
                          send_message(PAT, sender,"The quality of the image you uploaded doesn't look up to the mark, there will be a problem when it comes to printing")
                          send_message(PAT, sender,"It will be better if you upload a higher quality image")
                    
                          

                        
  print "Handling Messages"
  payload = request.get_data()
  print payload
  for sender, message in messaging_events(payload):
    print "Incoming from %s: %s" % (sender, message)
    w=["hi","hello","hey","new"]
    if message.lower() in w:
      send_message_welcome(PAT, sender)
    if "visiting" in message.lower() or "card" in message.lower():
      send_message_VC(PAT, sender) 
      change_product_type(sender,"VC")
    if "mugs" in message.lower():
      send_message(PAT, sender,"Please upload an image you wish to add on the Mug") 
      change_product_type(sender,"MG")
    if "cloth" in message.lower() or "clothes" in message.lower() or "shirt" in message.lower() or "tshirt" in message.lower():
      send_message(PAT, sender,"Please upload an image you wish to use")
      change_product_type(sender,"CL")
      
    

    
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text



def send_message_edit(token, recipient):
 
  message={

      "attachment":{
        "type":"template",
        "payload":{
          "template_type":"button",
          "text":"Why don't you try editing your image, or if you are ready, select 'Show'",
          "buttons":[
            {
              "type": "web_url",
        "url": "https://theblendsalon.com/cimpress/index-1.php?userid="+recipient,
        "title": "Edit",
        "webview_height_ratio": "full",
                "messenger_extensions": True,  
                "fallback_url": "https://theblendsalon.com/cimpress/index-1.php?userid="+recipient,
                
            },
            
              {
        "type":"postback",
        "title":"Show Products",
        "payload":"SHOW_OPTIONS"
      }
                
            
          ]
        }
      }
  }
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({

      "recipient": {"id": recipient},
      "message": message
      
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def send_message_welcome(token, recipient):
 
  message={

      "attachment":{
        "type":"template",
        "payload":{
          "template_type":"button",
          "text":"Hi, what are you looking for?",
          "buttons":[   
              {
        "type":"postback",
        "title":"Visiting Card",
        "payload":"VC"
      },
      {
        "type":"postback",
        "title":"Mugs",
        "payload":"MG"
      },
      {
        "type":"postback",
        "title":"Clothing",
        "payload":"CL"
      }

                
            
          ]
        }
      }
  }
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({

      "recipient": {"id": recipient},
      "message": message
      
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text    

def send_message_VC(token, recipient):
 
  message={

      "attachment":{
        "type":"template",
        "payload":{
          "template_type":"button",
          "text":"Do you have a logo?",
          "buttons":[   
              {
        "type":"postback",
        "title":"Yes",
        "payload":"YES_VC"
      },
      {
        "type":"postback",
        "title":"No",
        "payload":"NO_VC"
      }

                
            
          ]
        }
      }
  }
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({

      "recipient": {"id": recipient},
      "message": message
      
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text    

def send_message_redirect_cimpress(token,recipient):
 
  message={

      "attachment":{
        "type":"template",
        "payload":{
          "template_type":"button",
          "text":"Click here to make your customised visiting card",
          "buttons":[   
              {
        "type":"web_url",
        "url":"http://theblendsalon.com/cimpress/api.html",
        "title":"Create Visiting Card"
      }

                
            
          ]
        }
      }
  }
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({

      "recipient": {"id": recipient},
      "message": message
      
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text    

def send_message_image(token, recipient,link):
  message = {
    "attachment":{
      "type":"image",
      "payload":{
        "url":link
      }
    }
  }
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({

      "recipient": {"id": recipient},
      "message": message
      
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def product_slider(token,recipient, list_f):
  message={
          "attachment": {
              "type": "template",
              "payload": {
                  "template_type": "generic",
                  "elements": send_message_product_slider(list_f, len(list_f))
              }
          }
  }
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({

      "recipient": {"id": recipient},
      "message": message
      
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def share_location(token,recipient):
  message={
    "text":"Please share your location:",
    "quick_replies":[
      {
        "content_type":"location",
      }
    ]
  }
  r = requests.post("https://graph.facebook.com/v2.6/me/messages", params={"access_token": token}, data=json.dumps({"recipient": {"id": recipient},"message": message}),headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def get_contact_details(token, recipient):
  send_message(token,recipient,"If you wish to continue searching, just type 'NEW'")
  message={
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"generic",
        "elements":[
           {
            "title":"Reach us at",
            "image_url":"https://cimpress.com/wp-content/uploads/2014/04/Cimpress_Home_FTD-01.jpg",
            "subtitle":"Lalbaugh, Mumbai, Maharashtra, India",
            "buttons":[
              {
                "type":"web_url",
                "url":"https://vistaprint.in",
                "title":"View Website"
              },
              {
		"type": "element_share"
				
             },
             {
          "type":"phone_number",
          "title":"Call Representative",
          "payload":"+912267186718"
             }
              
            ]      
          }
        ]
      }
    }
  }

  r = requests.post("https://graph.facebook.com/v2.6/me/messages", params={"access_token": token}, data=json.dumps({"recipient": {"id": recipient},"message": message}),headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
      print r.text
    
if __name__ == '__main__':
  app.run()
