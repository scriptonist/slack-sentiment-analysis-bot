from slackclient import SlackClient
import os,time
from textblob import TextBlob as tb
from flask import Flask,request,Response

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')


app = Flask(__name__)


def list_channels():
    channels_call = slack_client.api_call("channels.list")
    if channels_call['ok']:
        return channels_call['channels']
    return None

def findId():
    channels = list_channels()
    if channels:
        for c in channels:
            if(c['name'] == 'team-convos'):
                return c['id'] 
    else:
        print("Unable to authenticate.")
        return None

def send_message(channel_id, message):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel_id,
        text=message,
        username='sentimeter',
        icon_emoji=':robot_face:'

    )


@app.route("/slack",methods=['post'])
def inbound():
    if request.form.get('token') == SLACK_WEBHOOK_SECRET and request.form.get('user_name') != "slackbot":
        channel = request.form.get('channel_name')
        username = request.form.get('user_name')
        text = request.form.get('text')
        sentiment = tb(text).sentiment
        pol = sentiment.polarity
        print(pol)
        if(pol >= 0.8):
            smiley = ":smile:"
        if(pol < 0.8 and pol >= 0.5):
            smiley = ":slightly_smiling_face:"
        if(pol < 0.5 and pol >= 0.3):
            smiley = ":slightly_frowning_face:"
        if(pol < 0.3 and pol >= 0.1):
            smiley = ":white_frowning_face:"
        if pol == 0:
            smiley = ":neutral_face:"
        if(pol < 0):
            smiley = ":cry:"
        inbound_message = username + " is feeling " + smiley
        send_message(findId(),inbound_message)
        print(inbound_message)
    return Response(),200

@app.route("/",methods=['GET'])
def test():
    return Response('It Works')

if __name__ == "__main__":
    app.run(debug=True)