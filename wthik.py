from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery

from flask import Flask, Response, request
from datetime import datetime, timedelta

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

import json
import os


app = Flask(__name__)
app.config.from_object('app_config')

client = Client()


def _build_service():
    scope = 'https://www.googleapis.com/auth/calendar.readonly'
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        keyfile_dict=app.config.get("SERVICE_ACCOUNT_INFO"),
        scopes=scope)
    service = discovery.build('calendar', 'v3', credentials=credentials)
    return service


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

    resp = MessagingResponse()
    resp.message(msg)
    return str(resp)


def _event_info(event):
    start = event['start'].get('date')
    end = event['end'].get('date')
    summary = event['summary']

    return "{} from {} to {}".format(summary, start, end)


def travel_schedule(service, calendar_id, num_events=5):
    now = datetime.utcnow()
    today = now.isoformat() + 'Z'
    tomorrow = (now + timedelta(days=1)).isoformat() + 'Z'

    # let google do the datetime math
    event_list = service.events().list(
        calendarId=calendar_id,
        timeMin=today,
        maxResults=num_events,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    event_response = ["My next five planned events are:\n"]

    for event in event_list.get("items", []):
        event_response.append(_event_info(event))

    msg = "\n".join(event_response)
    resp = MessagingResponse()
    resp.message(msg)
    return str(resp)


def help_response():
    resp = MessagingResponse()
    resp.message("""Ask me "Where is Kelley?" to see my current whereabouts or "Travel schedule" to see what's coming up.""")
    return str(resp)


@app.route("/sms", methods=["GET", "POST"])
def main():
    incoming_message = request.values.get("Body")
    troll(incoming_message)

    service = _build_service()
    calendar_id = app.config.get("CALENDAR_ID")

    normalized_message = incoming_message.lower()

    if "where" in normalized_message:
        return where_is_she(service, calendar_id)
    elif "full schedule" in normalized_message:
        return travel_schedule(service, calendar_id, 25)
    elif "schedule" in normalized_message:
        return travel_schedule(service, calendar_id)
    else:
        return help_response()



if __name__ == '__main__':
    app.run(debug=True)
