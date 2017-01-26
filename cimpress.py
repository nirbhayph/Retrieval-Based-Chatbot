from flask import Flask, request
import json
import requests


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
           
        if messaging_event.get("message"):
          
          for item,value in messaging_event["message"].iteritems():
              
                    
            if(str(item)=="attachments"):
                print item
                for mem,aea in value[0].iteritems(): 
                    if(mem=="payload"):
                       
                      image_url=str(aea["url"])
                      print image_url
                      send_message_new(PAT,sender,image_url)

                        
  print "Handling Messages"
  payload = request.get_data()
  print payload
  for sender, message in messaging_events(payload):
    print "Incoming from %s: %s" % (sender, message)
    if message=="hi":
      send_message_new(PAT, sender,image_url)
    
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



def send_message_new(token, recipient,image_url):

  HOST = "109.73.164.163"
  PORT = 3306
  USER = "root"
  PASSWORD = "root"
  DB = "cimpress"

  connection = db.Connection(host=HOST, port=PORT, user=USER, passwd=PASSWORD, db=DB)
  c = connection.cursor()
  c.execute("SELECT * FROM links")
  row=c.fetchall()
  for r in row:
    print r
  
  message={

      "attachment":{
        "type":"template",
        "payload":{
          "template_type":"button",
          "text":"Why don't you try editing your image",
          "buttons":[
            {
              "type": "web_url",
        "url": "https://theblendsalon.com/cimpress/index-1.php?url="+image_url,
        "title": "Edit",
        "webview_height_ratio": "compact",
                "messenger_extensions": True,  
                "fallback_url": "https://theblendsalon.com/cimpress/index-1.php?url="+image_url
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


if __name__ == '__main__':
  app.run()
