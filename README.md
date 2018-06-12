# Where The Hell Is Kelley?

Or, how I keep my mom updated on my travel schedule with Python, Twilio and Google Calendar. For a full tutorial on how to run this check out the blog post:

https://www.twilio.com/blog/2018/06/how-i-keep-my-mom-updated-on-my-travel-schedule-with-twilio-and-google-calendar.html

![](https://www.twilio.com/blog/wp-content/uploads/2018/06/Screen-Shot-2018-06-12-at-11.34.16-AM-1024x386.png)

## Deploying to Heroku

This project has some modifications not mentioned in the blog post to support deploying to Heroku. Make sure you have a Heroku account and [create a new project from the CLI](https://devcenter.heroku.com/articles/heroku-cli)

```heroku create```

Set the following as [Heroku environment variables](https://devcenter.heroku.com/articles/config-vars#set-a-config-var) with `heroku config:set VARIABLE_NAME:VARIABLE_VALUE`. You can also find the expected environment variables in [app_config.py](app_config.py).

```
CALENDAR_ID
WTHIK_PROJECT_ID
WTHIK_PRIVATE_KEY_ID
WTHIK_PRIVATE_KEY
WTHIK_CLIENT_EMAIL
WTHIK_CLIENT_ID
WTHIK_CLIENT_CERT_URL
```

One gotcha: make sure your [private key is formatted correctly](https://github.com/robinske/wthik/issues/1#issuecomment-396741043).

Deploy to Heroku:

```
git push heroku master
```

Once deployed, [update your Twilio webhook URL](https://www.twilio.com/blog/2018/06/how-i-keep-my-mom-updated-on-my-travel-schedule-with-twilio-and-google-calendar.html#h.rh3zgjz8i0qb) to point at your Heroku URL instead of an `ngrok` URL. Then test it out by sending an SMS!

![](https://pbs.twimg.com/media/DXpurHnW0AIOWie.jpg)

