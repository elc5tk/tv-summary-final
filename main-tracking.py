#!/usr/bin/env python3

import tweepy
from typing import Optional
import requests
import json
import logging
import time
import re
import os
from config import create_api


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def reply_to_tweets(api, keywords, since_id):
    print("retrieving and replying to tweets...")
    new_since_id = since_id
    mentions = api.mentions_timeline(
                since_id=since_id, 
                tweet_mode = 'extended')
    for mention in reversed(mentions):
        new_since_id = max(mention.id, new_since_id)
        print(str(mention.id) + " -- " + mention.full_text)
        
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

            if len(summary) > 250 and len(summary) < 520:
                summary1 = summary[3:249]
                summary2 = summary[249:len(summary)-4]
                api.update_status(status = "@" + mention.user.screen_name + " " + summary1, in_reply_to_status_id = mention.id)
                api.update_status(status = "@" + mention.user.screen_name + " " + summary2, in_reply_to_status_id = mention.id)
            elif len(summary) >= 520:
                summary1 = summary[3:249]
                summary2 = summary[249:499]
                summary3 = summary[499:len(summary)-4]
                api.update_status(status = "@" + mention.user.screen_name + " " + summary1, in_reply_to_status_id = mention.id)
                api.update_status(status = "@" + mention.user.screen_name + " " + summary2, in_reply_to_status_id = mention.id)
                api.update_status(status = "@" + mention.user.screen_name + " " + summary3, in_reply_to_status_id = mention.id)
            else:
                summary1 = summary[3:len(summary)-4]
                api.update_status(status = "@" + mention.user.screen_name + " " + summary1, in_reply_to_status_id = mention.id)

    return new_since_id


def main():
    api = create_api()
    since_id = 1
    while True:
        since_id = reply_to_tweets(api, ["summary"], since_id)
        logger.info("Waiting...")
        time.sleep(30)

if __name__ == "__main__":
    main()

# https://www.youtube.com/watch?v=W0wWwglE1Vc