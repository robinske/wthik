import os

SUBJECT = os.environ["CALENDAR_SUBJECT"]
CALENDAR_ID = os.environ["CALENDAR_ID"]
TRAVELER = "Kelley"

SERVICE_ACCOUNT_INFO = {
    u"type": "service_account",
    u"project_id": os.environ["WTHIK_PROJECT_ID"],
    u"private_key_id": os.environ["WTHIK_PRIVATE_KEY_ID"],
    u"private_key": os.environ["WTHIK_PRIVATE_KEY"],
    u"client_email": os.environ["WTHIK_CLIENT_EMAIL"],
    u"client_id": os.environ["WTHIK_CLIENT_ID"],
    u"auth_uri": "https://accounts.google.com/o/oauth2/auth",
    u"token_uri": "https://accounts.google.com/o/oauth2/token",
    u"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    u"client_x509_cert_url": os.environ["WTHIK_CLIENT_CERT_URL"]
}
