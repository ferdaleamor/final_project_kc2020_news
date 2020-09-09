import tweepy
import pandas as pd
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import numpy as np
import re
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import nltk
from wordcloud import WordCloud
from collections import Counter
from os import remove

nltk.download('stopwords')

# Variables that contains the user credentials to access Twitter API 
consumer_key= 'K8NPXvBbX1K1s918AXpc3RXAd'
consumer_secret= 'DtAvL4cKQKF4EFJP2LLt76djMyLUwfalhfC80vxpU8TpdfAq2I'
access_token= '1402881252-iOgU2CKhNaf6MexvFNTtSc1fBpc0mK2QyA3KR0R'
access_token_secret= 'RPrH5rFi6j7kRtBXQphFlZ2GG7fZRNiXNpydR17kiUGV0'

# Setup tweepy to authenticate with Twitter credentials:
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create the api to connect to twitter with your creadentials
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

def readTweeter(keyword,max_tweets,idiom, num):
    type_result = "recent" #"recent" "popular"
    searched_tweets = [status for status in tweepy.Cursor(api.search, q=keyword, tweet_mode="extended",
                                                      result_type= type_result, lang = idiom).items(max_tweets)]

    #Creating Dataframe of Tweets
    #Cleaning searched tweets and converting into Dataframe
    my_list_of_dicts = []
    
    for each_json_tweet in searched_tweets:
        my_list_of_dicts.append(each_json_tweet._json)

    with open(keyword + '.txt', 'w') as file:
            file.write(json.dumps(my_list_of_dicts, indent=4))

    my_demo_list = []
    with open(keyword + '.txt', encoding='utf-8') as json_file:  
        all_data = json.load(json_file)
        for each_dictionary in all_data:
            user = each_dictionary['user']['screen_name']
            location = each_dictionary['user']['location']
            language = each_dictionary['lang']
            text = each_dictionary['full_text']
            retweet_count = each_dictionary['retweet_count']
            followers_count = each_dictionary['user']['followers_count']
            geo_location = each_dictionary['geo']
            created_at = each_dictionary['created_at']
            my_demo_list.append({'num_topic' : num,
                                 'topic': keyword,
                                 'user': user,
                                 'location': str(location),
                                 'language': str(language),
                                 'text': str(text),
                                 'retweet_count': int(retweet_count),
                                 'followers_count': int(followers_count),
                                 'geo': geo_location,
                                 'created_at': created_at,
                                })

            tweet_dataset = pd.DataFrame(my_demo_list, columns = 
                                      ['num_topic', 'topic','user', 'location', 'language', 'text', 'retweet_count',
                                       'followers_count', 'geo_location', 'created_at'])

            #Pasamos el formato de la fecha que genera tweepy a formato datetime
            tweet_dataset['created_at'] = tweet_dataset['created_at'].astype('datetime64[ns]')             
            tweet_dataset['created_at'] = tweet_dataset.created_at.dt.to_pydatetime()

                    
    #Writing tweet dataset ti csv file for future reference
    #tweet_dataset.to_csv(keyword + '_tweet_data.csv',sep=';')
    return tweet_dataset

my_columns = ['num_topic','topic','user', 'location', 'language', 'text', 'retweet_count', 'followers_count', 'geo_location', 'created_at']
tweet_dataset = pd.DataFrame(columns = my_columns)

#Defining Search keyword and number of tweets and searching tweets

topic_words = pd.read_csv('../data/topic_today.csv')
query = list(topic_words['Topic'])

num_tweets = 20
language = 'es'
num_topic = 0
for topic in query:
    num_topic += 1
    tweet_dataset = tweet_dataset.append(readTweeter(topic,num_tweets,language, num_topic), ignore_index=True)

tweet_dataset_to_save = tweet_dataset.drop(['text'], axis = 'columns')       
tweet_dataset_to_save.to_csv('../data/tweet_dataset.csv', index=False)

for keyword in query:
    remove(keyword + '.txt')

