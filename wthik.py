from google.oauth2 import service_account
from apiclient import discovery

from flask import Flask, Response, request
from datetime import datetime, timedelta

from twilio.rest import Client

import json
import os


app = Flask(__name__)
app.config.from_object('app_config')

client = Client()


def _get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    SERVICE_ACCOUNT_INFO = app.config.get("SERVICE_ACCOUNT_INFO")

    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES,
        subject=app.config.get("SUBJECT"))

    return credentials


def _twiml_response(msg):
    twiml = """<Response><Message>{}</Message></Response>""".format(msg)
    return Response(twiml, mimetype="text/xml")


def troll(incoming_message):
    from_num = request.values.get("From")

    msg = None

    if from_num == os.environ.get("MY_MOTHER"):
        msg = "Hi Mom! I love you and I miss you too!"

    elif incoming_message == "KELLEY WHERE'S KELLEY" and from_num == os.environ.get("KAT"):
        msg = "I'm right behind you."

    if msg:
        client.api.account.messages.create(
            to=from_num,
            from_=os.environ["WTHIK_FROM"],
            body=msg)


def where_is_she(service, calendar_id):
    now = datetime.utcnow()
    today = now.isoformat() + 'Z'
    tomorrow = (now + timedelta(days=1)).isoformat() + 'Z'

    # let google do the datetime math
    currentEvent = service.events().list(
        calendarId=calendar_id,
        timeMin=today,
        timeMax=tomorrow,
        maxResults=1,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    currentlyTravelingTo = currentEvent.get('items', [])

    if not currentlyTravelingTo:
        futureEvents = service.events().list(
            calendarId=calendar_id,
            timeMin=today,
            maxResults=1,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        event = futureEvents.get('items', [])[0]
        start = event['start'].get('dateTime', event['start'].get('date'))
        msg = "Doesn't look like {} is currently traveling. Her next trip is to {} on {}".format(
            app.config.get("TRAVELER"),
            event['summary'],
            start)
    else:
        event = currentlyTravelingTo[0]
        end = event['end'].get('dateTime', event['end'].get('date'))
        msg = "{} is currently in {} until {}".format(
            app.config.get("TRAVELER"),
            event['summary'],
            end)

    return _twiml_response(msg)


def _event_info(event):
    start = event['start'].get('date')
    end = event['end'].get('date')
    summary = event['summary']

    return "{} from {} to {}".format(summary, start, end)


def travel_schedule(service, calendar_id):
    now = datetime.utcnow()
    today = now.isoformat() + 'Z'
    tomorrow = (now + timedelta(days=1)).isoformat() + 'Z'

    # let google do the datetime math
    event_list = service.events().list(
        calendarId=calendar_id,
        timeMin=today,
        maxResults=5,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    event_response = ["My next five planned events are:\n"]

    for event in event_list.get("items", []):
        event_response.append(_event_info(event))

    msg = "\n".join(event_response)
    return _twiml_response(msg)


def help_response():
    twiml = """
    <Response>
        <Message>
            Ask me "Where is Kelley?" to see my current whereabouts or "Travel schedule" to see what's coming up.
        </Message>
    </Response>
    """

    return Response(twiml, mimetype="text/xml")


@app.route("/sms", methods=["GET", "POST"])
def main():
    incoming_message = request.values.get("Body")
    troll(incoming_message)

    credentials = _get_credentials()
    service = discovery.build('calendar', 'v3', credentials=credentials)
    calendar_id = app.config.get("CALENDAR_ID")

    if "where" in incoming_message.lower():
        return where_is_she(service, calendar_id)
    elif "schedule" in incoming_message.lower():
        return travel_schedule(service, calendar_id)
    else:
        return help_response()



if __name__ == '__main__':
    app.run(debug=True)
