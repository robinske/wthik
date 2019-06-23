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


def notify(incoming_message):
    from_num = request.values.get("From")
    my_num = os.environ.get("MY_NUMBER")

    if from_num != my_num:
        msg = "New WTHIK message from {}: '{}'".format(from_num, incoming_message)
        client.api.account.messages.create(
            to=my_num,
            from_=os.environ["WTHIK_FROM"],
            body=msg)


def _subtract_one_day(date_str):
    # fix the off by one error, at least for US timezones
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt - timedelta(days=1)


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
        msg = "Doesn't look like {} is currently traveling. {} next trip is to {} on {}".format(
            app.config.get("TRAVELER"),
            app.config.get("PRONOUN"),
            event['summary'],
            start)
    else:
        event = currentlyTravelingTo[0]
        end = _subtract_one_day(event['end'].get('dateTime', event['end'].get('date'))).strftime("%B %d, %Y")
        msg = "{} is currently in {} until {}".format(
            app.config.get("TRAVELER"),
            event['summary'],
            end)

    resp = MessagingResponse()
    resp.message(msg)
    return str(resp)


def _event_info(event):
    start = event['start'].get('date')
    end = _subtract_one_day(event['end'].get('date')).strftime("%Y-%m-%d")
    summary = event['summary']

    return "{} from {} to {}".format(summary, start, end)


def travel_schedule(service, calendar_id):
    now = datetime.utcnow()
    today = now.isoformat() + 'Z'

    # let google do the datetime math
    event_list = service.events().list(
        calendarId=calendar_id,
        timeMin=today,
        maxResults=25,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    event_response = ["Here's my upcoming schedule:\n"]

    for event in event_list.get("items", []):
        event_response.append(_event_info(event))

    msg = "\n".join(event_response)
    resp = MessagingResponse()
    resp.message(msg)
    return str(resp)


def help_response():
    resp = MessagingResponse()
    msg = """Ask me "Where's {}?" to see my current whereabouts or "Schedule" to see what's coming up.""".format(
        app.config.get("TRAVELER"),
        )
    resp.message(msg)
    return str(resp)


@app.route("/sms", methods=["GET", "POST"])
def main():
    incoming_message = request.values.get("Body")
    service = _build_service()
    calendar_id = app.config.get("CALENDAR_ID")

    normalized_message = incoming_message.lower()
    notify(normalized_message)

    if "where" in normalized_message:
        return where_is_she(service, calendar_id)
    elif "schedule" in normalized_message:
        return travel_schedule(service, calendar_id)
    else:
        return help_response()
