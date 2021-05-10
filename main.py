#!/usr/bin/env python3

import tweepy
from typing import Optional
import requests
import json
import logging
import time
import re
import os

#consumer_key = os.getenv("CONSUMER_KEY")
#consumer_secret = os.getenv("CONSUMER_SECRET")
#access_token = os.getenv("ACCESS_TOKEN")
#access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

consumer_key = "ET6dYo1qjkqwy19Cwbhns9dKI"
consumer_secret = "TTzHLPq34e5NOswyXYjZOjXHegmGhiQOgDAQDGSelSQ6JPOMuA"
access_token = "1338684727826452480-ThQ1pXvmjbFqUlH5lmWZ9yGWqEIgz6"
access_token_secret = "hwP68hjJGMRq8xE141jqbaY8W1Hl4vatYJiMKBjouoq8w"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

FILE_NAME = "last_seen_id.txt"

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, "r")
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, "w")
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def reply_to_tweets():
    print("retrieving and replying to tweets...")
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(
                last_seen_id, 
                tweet_mode = 'extended')
    for mention in reversed(mentions):
        print(str(mention.id) + " -- " + mention.full_text)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if "summary" in mention.full_text.lower():
            print("Found tweet!")
            print("Responding")

            tweet = mention.full_text

            #clean string
            pat = re.compile(r'[^a-zA-Z0-9 ]+')
            tweet = re.sub(pat, '', tweet).lower()

            #split string
            tweet_words = tweet.split()

            # https://pythonexamples.org/python-iterate-over-words-of-string/
            # https://stackoverflow.com/questions/24628799/find-and-print-index-of-element-in-a-list-string

            episodeWord_index = tweet_words.index("episode")
            episodeNumber_index = episodeWord_index + 1
            episode = tweet_words[episodeNumber_index]

            seasonWord_index = tweet_words.index("season")
            seasonNumber_index = seasonWord_index + 1
            season = tweet_words[seasonNumber_index]

            if "of" in tweet:
                    ofWord_index = tweet_words.index("of")
                    showNumber_index_start =  ofWord_index + 1
                    showNumber_index_end = seasonWord_index
                    if showNumber_index_start == showNumber_index_end:
                        show_title = tweet_words[showNumber_index_start]
                    else:
                        showNumber_index_end = seasonWord_index - 1
                        show_title = tweet_words[showNumber_index_start:showNumber_index_end]
            else:
                    showNumber_index_end = seasonWord_index
                    show_title = tweet_words[2:showNumber_index_end]

            url = "http://api.tvmaze.com/singlesearch/shows?q=:" + str(show_title)
            response = requests.get(url)
            if response.status_code != 200:
                api.update_status(status = "@" + mention.user.screen_name + " Sorry! We don't have that show or we don't understand what you are asking. Please try again!", in_reply_to_status_id = mention.id)
                break
            responseText = (response.text)
            responseTextDict = json.loads(responseText)

            showID = responseTextDict["id"]

            url2 = "http://api.tvmaze.com/shows/" + str(showID) + "/episodebynumber?season=" + str(season) + "&number=" + str(episode)
            response2 = requests.get(url2)
            if response2.status_code != 200:
                api.update_status(status = "@" + mention.user.screen_name + " Sorry! That episode or season might not exist or we don't understand what you are asking. Please try again!", in_reply_to_status_id = mention.id)
                break
            responseText2 = (response2.text)
            responseText2Dict = json.loads(responseText2)
            summary = (responseText2Dict["summary"])

            if len(summary) > 270 and len(summary) < 540:
                summary1 = summary[3:259]
                summary2 = summary[259:len(summary)-4]
                api.update_status(status = "@" + mention.user.screen_name + " " + summary1, in_reply_to_status_id = mention.id)
                api.update_status(status = "@" + mention.user.screen_name + " " + summary2, in_reply_to_status_id = mention.id)
            elif len(summary) >= 540:
                summary1 = summary[3:259]
                summary2 = summary[259:520]
                summary3 = summary[520:len(summary)-4]
                api.update_status(status = "@" + mention.user.screen_name + " " + summary1, in_reply_to_status_id = mention.id)
                api.update_status(status = "@" + mention.user.screen_name + " " + summary2, in_reply_to_status_id = mention.id)
                api.update_status(status = "@" + mention.user.screen_name + " " + summary3, in_reply_to_status_id = mention.id)
            else:
                summary1 = summary[3:len(summary)-4]
                api.update_status(status = "@" + mention.user.screen_name + " " + summary1, in_reply_to_status_id = mention.id)


while True:
    reply_to_tweets()
    time.sleep(2)

# https://www.youtube.com/watch?v=W0wWwglE1Vc