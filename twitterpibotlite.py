import os
import webbrowser
import pickle
from apscheduler.schedulers.background import BackgroundScheduler
from twython import TwythonStreamer
from twython.api import Twython

import cv2  # https://jjyap.wordpress.com/2014/05/24/installing-opencv-2-4-9-on-mac-osx-with-python-support/


import logging
logging.basicConfig()

scheduler = BackgroundScheduler()
responses = []


class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        for response in responses:
            response(data)


def authenticate():
    token_dir = "temp" + os.sep + "tokens" + os.sep

    if not os.path.exists(token_dir):
        os.makedirs(token_dir)

    app_key_path = token_dir + "APP_KEY.pkl"
    app_secret_path = token_dir + "APP_SECRET.pkl"
    final_oauth_token_path = token_dir + "FINAL_OAUTH_TOKEN.pkl"
    final_oauth_token_secret_path = token_dir + "FINAL_OAUTH_TOKEN_SECRET.pkl"

    exists = os.path.isfile(app_key_path) and os.path.isfile(app_secret_path)

    if exists:
        app_key = pickle.load(open(app_key_path, "rb"))
        app_secret = pickle.load(open(app_secret_path, "rb"))
    else:
        app_key = raw_input("Enter your APP_KEY:")
        app_secret = raw_input("Enter your APP_SECRET:")

        pickle.dump(app_key, open(app_key_path, "wb"))
        pickle.dump(app_secret, open(app_secret_path, "wb"))

    exists = os.path.isfile(final_oauth_token_path) and os.path.isfile(final_oauth_token_secret_path)

    if exists:

        final_oauth_token = pickle.load(open(final_oauth_token_path, "rb"))
        final_oauth_token_secret = pickle.load(open(final_oauth_token_secret_path, "rb"))

    else:

        t = Twython(app_key, app_secret)

        auth = t.get_authentication_tokens()

        oauth_token = auth["oauth_token"]
        oauth_token_secret = auth["oauth_token_secret"]

        url = auth["auth_url"]
        webbrowser.open(url)

        oauth_verifier = raw_input("Enter your pin:")

        t = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

        final_step = t.get_authorized_tokens(oauth_verifier)

        final_oauth_token = final_step["oauth_token"]
        final_oauth_token_secret = final_step["oauth_token_secret"]

        pickle.dump(final_oauth_token, open(final_oauth_token_path, "wb"))
        pickle.dump(final_oauth_token_secret, open(final_oauth_token_secret_path, "wb"))

    return [app_key, app_secret, final_oauth_token, final_oauth_token_secret]


def add_scheduled_job(func, trigger):
    scheduler.add_job(func, trigger)


def add_response(func):
    responses.append(func)


def start_schedule():
    scheduler.start()


def start_stream():
    stream.user()


def stop_schedule():
    scheduler.shutdown()


def stop_stream():
    stream.disconnect()


def take_photo():
    print("taking photo")
    for i in range(20):
        file_path = "photo%s.jpg" % i
        err, image = camera.read()
        cv2.imwrite(file_path, image)
    return file_path


def upload(file_path):
    f = None
    try:
        print("uploading photo")
        f = open(file_path, 'rb')
        media = twitter.upload_media(media=f)
        media_id = media["media_id_string"]
        print ("media id %s" % media_id)
        return media_id
    finally:
        if f:
            f.close()


def tweet(text=None, media_id=None, in_reply_to_status_id = None):
    media_ids=None
    if media_id:
        media_ids=[media_id]
    twitter.update_status(status=text, media_ids=media_ids, in_reply_to_status_id = in_reply_to_status_id)


tokens = authenticate()
twitter = Twython(app_key=tokens[0], app_secret=tokens[1], oauth_token=tokens[2], oauth_token_secret=tokens[3])
stream = MyStreamer(app_key=tokens[0], app_secret=tokens[1], oauth_token=tokens[2], oauth_token_secret=tokens[3])

camera = cv2.VideoCapture(0)

take_photo()


def start():
    start_schedule()
    start_stream()


def stop():
    stop_schedule()
    stop_stream()
    camera.release()
    exit(0)
