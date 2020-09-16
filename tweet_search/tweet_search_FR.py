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
consumer_key= 'your_key'
consumer_secret= 'your_key'
access_token= 'your_key'
access_token_secret= 'your_key'

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
        global tweet_dataset
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

topic_words = pd.read_csv('../data/topic_today_FR.csv')
query = list(topic_words['Topic'])

num_tweets = 1000
language = 'fr'
num_topic = 0
for topic in query:
    num_topic += 1
    tweet_dataset = tweet_dataset.append(readTweeter(topic,num_tweets,language, num_topic), ignore_index=True)

for keyword in query:
    remove(keyword + '.txt')

analyzer = SentimentIntensityAnalyzer()
tweet_dataset['compound'] = [analyzer.polarity_scores(x)['compound'] for x in tweet_dataset['text']]
tweet_dataset['neg'] = [analyzer.polarity_scores(x)['neg'] for x in tweet_dataset['text']]
tweet_dataset['neu'] = [analyzer.polarity_scores(x)['neu'] for x in tweet_dataset['text']]
tweet_dataset['pos'] = [analyzer.polarity_scores(x)['pos'] for x in tweet_dataset['text']]

pos = [j for i, j in enumerate(tweet_dataset['text']) if tweet_dataset['compound'][i] > 0.15]
neu = [j for i, j in enumerate(tweet_dataset['text']) if 0.15>= tweet_dataset['compound'][i] >= -0.15]
neg = [j for i, j in enumerate(tweet_dataset['text']) if tweet_dataset['compound'][i] < -0.15]

#calculamos el tamañao del cada porcion del pie
size_pos = ((len(pos)*100)/len(tweet_dataset))*10
size_neg = ((len(neg)*100)/len(tweet_dataset))*10
size_neu = ((len(neu)*100)/len(tweet_dataset))*10

def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)
     
    return input_txt 

tweet_dataset['text'] = np.vectorize(remove_pattern)(tweet_dataset['text'], "@[\w]*")

tweet_dataset_to_save = tweet_dataset.drop(['text'], axis = 'columns')

tweet_dataset_to_save.to_csv('../data/tweet_dataset_FR.csv')

