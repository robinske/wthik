from google.oauth2 import service_account
from apiclient import discovery

from flask import Flask, Response

from datetime import datetime, timedelta
import json


app = Flask(__name__)
app.config.from_object('app_config')


def _get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    SERVICE_ACCOUNT_INFO = app.config.get("SERVICE_ACCOUNT_INFO")

    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES,
        subject=app.config.get("SUBJECT"))

    return credentials


@app.route("/sms", methods=["GET", "POST"])
def main():
    credentials = _get_credentials()
    service = discovery.build('calendar', 'v3', credentials=credentials)

    now = datetime.utcnow()
    today = now.isoformat() + 'Z'
    tomorrow = (now + timedelta(days=1)).isoformat() + 'Z'

    calendar_id = app.config.get("CALENDAR_ID")

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

    twiml = """<Response><Message>{}</Message></Response>""".format(msg)

    return Response(twiml, mimetype="text/xml")


if __name__ == '__main__':
    app.run(debug=True)
