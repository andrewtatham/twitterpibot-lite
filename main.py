import datetime
from pprint import pprint
from apscheduler.triggers.cron import CronTrigger
import twitterpibotlite as t


def tweet_time():
    text = ""
    text += datetime.datetime.now().strftime("%c")
    t.tweet(text=text)


def tweet_photo():
    photo = t.take_photo()
    media_id = t.upload(photo)
    t.tweet(media_id=media_id)


# Responses...
def print_data_response(data):
    if "text" in data:
        tweet = data
        sender = tweet["user"]
        print("Tweet: " + sender["name"] + " [@" + sender["screen_name"] + "] - " + tweet["text"])

    elif "direct_message" in data:
        dm = data["direct_message"]
        sender = dm["sender"]
        print("Direct Message: " + sender["name"] + " [@" + sender["screen_name"] + "] - " + dm["text"])

    elif "event" in data:

        event = data["event"]
        source = event["source"]
        target = event["target"]

        text = "Event:"
        text += " Source:" + source["name"] + " @" + source["screen_name"]
        text += " Target:" + target["name"] + " @" + target["screen_name"]

        if "target_object" in event:
            target_object = event["target_object"]
            if "id_str" in target_object:
                text += " Id: " + target_object["id_str"]
            if "text" in target_object:
                text += " Text: " + target_object["text"]

        print(text)

    elif "friends" in data:
        print("Connected...")

    else:
        pprint(data)


def time_response(data):
    if "text" in data and "time" in data["text"]:
        text = data["user"]["screen_name"] + " "
        text += datetime.datetime.now().strftime("%c")
        reply_to_status_id = data["id_str"]
        t.tweet(text=text, reply_to_status_id=reply_to_status_id)


def photo_response(data):
    if "text" in data and "photo" in data["text"]:
        text = data["user"]["screen_name"]
        reply_to_status_id = data["id_str"]
        photo = t.take_photo()
        media_id = t.upload(photo)
        t.tweet(text=text, media_id=media_id, reply_to_status_id=reply_to_status_id)


def stop_response(data):
    if "user" in data and data["user"]["screen_name"] == "andrewtatham" and "text" in data and "stop" in data["text"]:
        print("STOPPING")
        t.stop_schedule()
        t.stop_stream()
        exit(0)


t.add_scheduled_job(func=tweet_time, trigger=CronTrigger(minute="*/2"))
t.add_scheduled_job(func=tweet_photo, trigger=CronTrigger(minute="*/5"))

t.add_response(print_data_response)
# t.add_response(time_response)
# t.add_response(photo_response)
# t.add_response(stop_response)

t.start_schedule()
t.start_stream()
