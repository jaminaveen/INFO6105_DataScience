import numpy as np
import pandas as pd
from lyrics_api import *
import requests
from bs4 import BeautifulSoup
import urllib
import urllib.request
from googletrans import Translator
from tensorflow import keras
import vectorize_data
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re



# Declaring global variables


# This method is to allow to call from other python file
def dummy_main(song_nos):
    href_list = []
    icon_list = []
    song_name_list = []
    artist_name_list = []
    lyrics_list = []
    artist_ref_list = []
    column_list = ['title', 'artist', 'lyrics_url', 'lyrics', 'icon_url', 'mood', 'artist_url']
    songs_df = pd.DataFrame(columns=column_list)
    lyricsScrapper_urls(href_list,icon_list,song_name_list,artist_name_list,artist_ref_list,song_nos)  # scrape urls and other songs info
    song_lyrics_srape(href_list,icon_list,song_name_list,artist_name_list,lyrics_list, artist_ref_list)  # scrape lyrics
    create_df(href_list,icon_list,song_name_list,artist_name_list,lyrics_list,songs_df, artist_ref_list)  # make the dataframe
    new_df = predict_top_k_list(songs_df)
    return new_df
#Write a method to run scrapper to scrape top 40 songs name and artist name and store in list
def lyricsScrapper_urls(href_list,icon_list,song_name_list,artist_name_list,artist_ref_list,song_nos):
    url = "https://www.musixmatch.com"
    headers = {'User-Agent':'Mozilla/5.0'}
    req = requests.get(url+'/explore', headers=headers)

    parser = BeautifulSoup(req.text, 'html.parser')
    links_for_lyrics = parser.find_all('h2', {'class': 'media-card-title'})
    artist_name = parser.find_all('h3', {'class': 'media-card-subtitle'})
    url_for_icon = parser.find_all('div', {'class': 'media-card-picture'})
    for count,links in enumerate(links_for_lyrics):
        if count < int(song_nos):
            anchor = links.find('a')
            song_name_list.append(anchor.text)
            href = anchor['href']
            href_list.append(url+href)
    for count1,icon in enumerate(url_for_icon):
        if count1 < int(song_nos):
            icon_url = icon.find('img')['srcset']
            icon_list.append(icon_url[0:68])
    for count2,artist in enumerate(artist_name):
        if count2 < int(song_nos):
            art = artist.find('a')
            artist_name_list.append(art.text)
            artist_ref = art['href']
            artist_ref_list.append(url+artist_ref)

# THis method can scrape lyrics for each song and append it in list
def song_lyrics_srape(href_list,icon_list,song_name_list,artist_name_list,lyrics_list, artist_ref_list):
    len_song = len(song_name_list)
    for i in range(0, len_song):
        api_call = base_url + lyrics_matcher + format_url + artist_search_parameter + artist_name_list[
            i] + track_search_parameter + song_name_list[i] + api_key
        request = requests.get(api_call)
        data = request.json()
        data = data['message']['body']
        lyrics_list.append(data['lyrics']['lyrics_body'])

# This method writes songs data into CSV
def create_df(href_list,icon_list,song_name_list,artist_name_list,lyrics_list,songs_df, artist_ref_list):
    songs_df['title'] = song_name_list
    songs_df['artist'] = artist_name_list
    songs_df['lyrics_url'] = href_list
    songs_df['icon_url'] = icon_list
    songs_df['lyrics'] = lyrics_list
    songs_df['artist_url'] = artist_ref_list
    return songs_df

# This method can get 30% lyrics by api call which needs artist name and song name as parameters
def get_lyrics_by_api_call(song_name, artist_name):
    try:
        # initializing for making a dataframe
        href_list = []
        icon_list = []
        song_name_list = []
        artist_name_list = []
        lyrics_list = []
        artist_ref_list =[]
        column_list = ['title', 'artist', 'lyrics_url', 'lyrics', 'icon_url', 'mood', 'artist_url']
        songs_df = pd.DataFrame(columns=column_list)
        song_name_list.append(song_name)
        artist_name_list.append(artist_name)
        artist_name = artist_name
        track_name = song_name
        api_call = base_url + lyrics_matcher + format_url + artist_search_parameter + artist_name + track_search_parameter + track_name + api_key
        request = requests.get(api_call)
        data = request.json()
        data = data['message']['body']
        lyrics = data['lyrics']['lyrics_body']
        lyrics_list.append(format(lyrics))
        # creating dataframe
        songs_df['title'] = song_name_list
        songs_df['artist'] = artist_name_list
        songs_df['lyrics'] = lyrics_list
        new_df = predict_top_k_list(songs_df)
        return new_df
    except Exception as e:
        raise e


def predict_top_k_list(topklistdf):
    top_k_lyrics = topklistdf['lyrics']
    training_set = pd.read_csv('train_lyrics_1000.csv',encoding='UTF-8')
    training_set['mood'] = training_set['mood'].apply(lambda x:1 if x=='happy' else 0)
    x_train, x_top_k_list = vectorize_data.ngram_vectorize(training_set['lyrics'],training_set['mood'],top_k_lyrics)
    new_model = keras.models.load_model('song_mood_mlp_model.h5')
    predicted_mood=new_model.predict(x_top_k_list)
    topklistdf['predicted']= predicted_mood
    topklistdf['mood'] = topklistdf['predicted'].apply(lambda x: 'Happy' if x>=(0.50) else 'Sad')
    topklistdf['probability'] = topklistdf['predicted'].apply(lambda x: x*100 if x>=(0.50) else 100*(1-x))
    return topklistdf

def replace_special_chars(i):
  i=i.split('\n')
  i=' '.join(i)
  a = re.sub('[^A-Za-z]+',' ',str(i))
  a = a.lower()
  return a

def word_cloud(topklistdf):

    topklistdf['lyrics']= topklistdf['lyrics'].apply(lambda x:replace_special_chars(x))
    df_happy = topklistdf.loc[topklistdf['mood'] == 'Happy', :]
    df_sad = topklistdf.loc[topklistdf['mood'] == 'Sad', :]
    happy_list = df_happy['lyrics'].tolist()
    sad_list = df_sad['lyrics'].tolist()


    str_happy = ""
    str_sad = ""

    #a = songs_df['lyrics'].tolist()
    for happy in happy_list:
       str_happy = str_happy + happy

    for sad in sad_list:
       str_sad = str_sad +sad

    wordcloud_happy = WordCloud(width = 1000, height = 500).generate(str_happy)
    plt.figure(figsize=(15,8))
    #plt.imshow(wordcloud_happy)
    plt.axis("off")
    plt.savefig("happy"+".png", bbox_inches='tight')
    # plt.show()
    # plt.close()

    wordcloud_sad = WordCloud(width = 1000, height = 500).generate(str_sad)
    plt.figure(figsize=(15,8))
    #plt.imshow(wordcloud_sad)
    plt.axis("off")
    plt.savefig("sad"+".png", bbox_inches='tight')
    # plt.show()
    # plt.close()

if __name__=="__main__":
    dummy_main()
