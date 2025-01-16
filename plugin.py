from datetime import datetime, timezone

import discord
import commands
import json
import seleniumscraper as ss
import queue
import schedule
import time
import traceback
import threading

client : discord.Client = None # will be passed in when plugin is loaded
lasts = {}
msgqueue = queue.Queue()

with open("config.json") as f:
    config = json.load(f)
    twitters = config["users"]

for user in twitters:
    lasts[user["handle"]] = datetime.now().timestamp()

session = ss.SeleniumSession(config["twitter"], driverpath=config["driverpath"], headless=True)
session.login()

lock = False

checked = {}
olds = set()

def do_the_thing():
    global session, lock, olds, first

    if lock:
        return

    try:
        lock = True
        templast = datetime.now().timestamp()

        for twitter in twitters:
            user = twitter["handle"]
            user_ = user.replace("_", "\\_")
            channelid = twitter["channel"]
            channel = client.get_channel(int(channelid))
            tweets = session.get_latest_tweets(user)
            if not tweets:
                print("uh oh something broke, resetting")
                session.driver.quit()
                session = ss.SeleniumSession(config["twitter"], driverpath=config["driverpath"], headless=True)
                session.login()
                return
            sent = False
            # tweets is a list of (tweet, time) tuples
            for (tweet, stamp) in tweets:
                stamp = stamp.replace("Z", "000")  # convert ms to us
                tweet = tweet.replace("://tw", "://vxtw")
                tweet = tweet.replace("://x.", "://fixvx.")
                posted = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S.%f").replace(
                    tzinfo=timezone.utc).timestamp()
                if user in tweet.lower():
                    # this is a tweet (not a retweet)
                    if user in lasts and lasts[user] <= posted and tweet not in olds:
                        olds.add(tweet)
                        message = f"{user_} tweeted {tweet}"
                        print("I am NOT sending ", channel.id, ": ", message)
                        msgqueue.put((channel, message))
                        sent = True
                else:
                    # this is a retweet
                    # we cant go by time, so check The List
                    if user not in checked:
                        # this is the first time checking, so mark every retweet as Old and don't post them
                        olds.add(tweet)
                    else:
                        if tweet not in olds:
                            olds.add(tweet)
                            message = f"{user_} retweeted {tweet}"
                            print("I am NOT sending ", channel.id, ": ", message)
                            continue
                            try:
                                msgqueue.put((channel,message))
                            except Exception:
                                print("Failed to send :(")
                            sent = True
            if len(tweets) > 0:
                checked[user] = True
            if sent:
                lasts[user] = templast

    except:
        raise
    finally:
        lock = False

schedule.every(30).seconds.do(do_the_thing)

@commands.registerEventHandler(triggerType="\\timeTick", name="sendqueuedmessages")
async def sendQueuedMessages():
    while not msgqueue.empty():
        channel, message = msgqueue.get(block=False)
        await channel.send(message)

def worker_main(depth=0):
    print("Schedule loop starting!")
    crashes = 0
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception:
            crashes += 1
            traceback.print_exc()
            print("Can't kill me, glowies! Recovering from crash #" + str(crashes))
            time.sleep(10)

job_thread = threading.Thread(target=worker_main)
job_thread.start()