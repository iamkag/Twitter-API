import datetime
import os
import tweepy
import pandas as pd
from utilities import *
import settings
import mysql.connector
import re
from geopy.geocoders import Nominatim
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import time
import psycopg2

max_results=200
month=1
achive_goal=False
rep=0

def create_stats(database_name):
    db_connection_str = 'postgresql+psycopg2://<ENTER-YOUR-CREDENTIALS>'
    db_connection = create_engine(db_connection_str)
    df = pd.read_sql_table(database_name, con=db_connection)
    print(df)
    print("Database READ")

    hist = px.histogram(df['track_word'], x='track_word', labels={'x': 'Track Words',
                                                                  'y': 'Counts'})
    print("Histogram DONE")

    counts_per_month = df['created_at'].groupby(df.created_at.dt.to_period("M")).agg('count')
    x_axes = []
    for item in counts_per_month.index:
        x_axes.append(item.strftime('%m'))
    y_axes = counts_per_month.values
    line_plot = px.line(x=x_axes, y=y_axes, labels={'x': 'Months',
                                                    'y': 'Number Of References'})

    countries_count = {}
    names = []
    count = []
    df_countries = df.groupby(by="country")
    for key, value in df_countries.country.groups.items():
        names.append(key)
        count.append(value.size)

    countries_count['Name'] = names
    countries_count['Count'] = count

    df_countries_count = pd.DataFrame(countries_count)
    df_world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    df_world_countries_count = df_world.merge(df_countries_count, how="left", left_on=['name'], right_on=['Name'])

    world_fig = px.choropleth(df_world_countries_count, locations="iso_a3",
                              color="Count",  # lifeExp is a column of gapminder
                              hover_name="Name",  # column to add to hover information
                              color_continuous_scale=px.colors.sequential.Plasma)
    print("WorldFig DOne")
    return world_fig, hist, line_plot


def coordinates_to_country(long, lat):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(str(lat) + "," + str(long), language='en')
    address = location.raw['address']
    return address.get('country', '')


def clean_tweet(self, tweet):
    '''
    Use sumple regex statemnents to clean tweet text by removing links and special characters
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) \
                                |(\w+:\/\/\S+)", " ", tweet).split())


def deEmojify(text):
    '''
    Strip all non-ASCII characters to remove emoji characters
    '''
    if text:
        return text.encode('ascii', 'ignore').decode('ascii')
    else:
        return None


def createDB(database_name):
    mydb = psycopg2.connect(
        "dbname='<YOUR-CREDENTIALS>' user='<YOUR-CREDENTIALS>' host='<YOUR-CREDENTIALS>' password='<YOUR-CREDENTIALS>'"
    )

    mycursor = mydb.cursor()
    mycursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(database_name))
    print(type(database_name))
    if mycursor.fetchone()[0] != 1:
        mycursor.execute("CREATE TABLE {} ({})".format(database_name, settings.TABLE_ATTRIBUTES))
        mydb.commit()
    else:
        mycursor.execute("DROP TABLE " + settings.TABLE_NAME)
        mycursor.execute("CREATE TABLE {} ({})".format(database_name, settings.TABLE_ATTRIBUTES))
        mydb.commit()
    mycursor.close()
    return mydb


def check_if_retweet(tweet):
    return tweet.text.startswith("RT")


def check_geo_exists(tweet):
    try:
        if tweet.geo['coordinates'] != None and tweet.geo['place_id'] != None:
            return True
        else:
            return False
    except:
        return False


def write_to_db(mydb, tweet, word,database_name):
    country = coordinates_to_country(tweet.geo['coordinates']['coordinates'][0],
                                     tweet.geo['coordinates']['coordinates'][1])
    mycursor = mydb.cursor()
    sql = f"INSERT INTO {database_name} (id_str,track_word, text, author_id, created_at, user_location,longitude, latitude, country,  language) VALUES (%s, %s,%s, %s, %s, %s,%s,%s, %s,%s)"
    val = (tweet.id, word, tweet.text[:250], tweet.author_id, tweet.created_at, tweet.geo['place_id'],
           tweet.geo['coordinates']['coordinates'][0], tweet.geo['coordinates']['coordinates'][1], country,
           tweet.lang)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()

def check_for_stop( my_tweets):

    global month
    global max_results
    global achive_goal
    global rep
    print("In",month,my_tweets,achive_goal)

    if rep ==2:
        return "Stop"
    if achive_goal and my_tweets >= max_results:
        return "Stop"

    if month >= 12:
        if my_tweets < max_results:
            month = 1
            achive_goal = True
            rep+=1
        else:
            return "Stop"
    else:
        return "Go"


def twitter_procedure(search_word, year=2021):
    database_name= 'local_search_'+str(year)
    print(type(database_name))
    api_key, api_key_secret, access_token, access_token_secret, bearer_token = get_tokens('Keys-Tokens.txt')

    client = tweepy.Client(bearer_token=bearer_token)
    mydb = createDB(database_name)

    my_islands = {}
    tweet_fields = ['id', 'text', 'author_id', 'created_at', 'geo', 'lang']
    my_tweets = 0
    my_ids = []

    global month
    global max_results
    global achive_goal
    month = 1
    max_results = 200
    achive_goal = False

    while True:

        for word in search_word:
            print(word)
            response = client.search_all_tweets(word, end_time=datetime.datetime(year, month + 1, 1),
                                                max_results=200, start_time=datetime.datetime(year, month, 1),
                                                tweet_fields=tweet_fields)
            time.sleep(10)
            tweets = response.data
            for tweet in tweets:
                if tweet.id not in my_ids:
                    if not check_if_retweet(tweet) and check_geo_exists(tweet):
                        write_to_db(mydb, tweet, word,database_name)
                        my_ids.append(tweet.id)
                        my_tweets += 1
        month += 1
        status= check_for_stop(my_tweets)
        print("Out",month, my_tweets, achive_goal)
        if status =="Stop":
            break


    world_fig, hist, line_plot = create_stats(database_name)
    print("DONE")

    return world_fig, hist, line_plot

