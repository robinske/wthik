# Where The Hell Is Kelley

## Instructions for running this yourself

Clone this repo

Follow the instructions from Google to create a service account: https://developers.google.com/api-client-library/python/auth/service-accounts

Add your credentials as `service-secret.json` in the project folder

Add `CALENDAR_SUBJECT` and `CALENDAR_ID` as environment variables

Create a Twilio account if you don't already have one and purchase a number: https://www.twilio.com/console/phone-numbers/search

run the application:

`python wthik.py`

run [ngrok](https://ngrok.com/):

`ngrok http 5000`

copy your ngrok url and paste it in your Twilio phone number configuration as a webhook when `A MESSAGE COMES IN`

Send a text to that number and et voila:

![](https://pbs.twimg.com/media/DXpurHnW0AIOWie.jpg)

