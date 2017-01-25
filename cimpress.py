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
  payload = request.get_data()
  print payload
  for sender, message in messaging_events(payload):
    print "Incoming from %s: %s" % (sender, message)
    if message=="hi":
      send_message_new(PAT, sender)
    else:  
      send_message(PAT, sender, message)
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



def send_message_new(token, recipient):
 
  message={
  "setting_type" : "call_to_actions",
  "thread_state" : "existing_thread",
  "call_to_actions":[
    {
      "type":"postback",
      "title":"Help",
      "payload":"DEVELOPER_DEFINED_PAYLOAD_FOR_HELP"
    },
    {
      "type":"postback",
      "title":"Start a New Order",
      "payload":"DEVELOPER_DEFINED_PAYLOAD_FOR_START_ORDER"
    },
    {
      "type":"web_url",
      "title":"Checkout",
      "url":"http://petersapparel.parseapp.com/checkout",
      "webview_height_ratio": "full",
      "messenger_extensions": true
    },
    {
      "type":"web_url",
      "title":"View Website",
      "url":"http://petersapparel.parseapp.com/"
    }
  ]
  }

  r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings",
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
