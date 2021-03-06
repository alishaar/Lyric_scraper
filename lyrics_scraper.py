# -*- coding: utf-8 -*-
"""lyrics_scraper.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FHuLFfoEoAVWb2I1v7stRVT7m86FemxL
"""





!pip install bs4

import requests
from bs4 import BeautifulSoup
import sys
import re
import os
import base64
from urllib.parse import urlencode

from google.colab import drive
drive.mount('/content/drive')
import sys
sys.path.append('/content/drive/My Drive/Colab Notebooks')
import configs



def getSpotifyToken():
  tokenURL = "https://accounts.spotify.com/api/token"
  tokenData={"grant_type": "client_credentials"} 
  clientCred= f"{configs.clientID}:{configs.clientSecret}"
  clientCred64=base64.b64encode(clientCred.encode())
  tokenHeader={"Authorization": f"Basic {clientCred64.decode()}"}
  token = requests.post(tokenURL, data=tokenData, headers=tokenHeader).json()['access_token']
  return str(token)

def getArtistId(name,apiToken):
  headers = {'Authorization': 'Bearer ' + apiToken}
  url = "https://api.spotify.com/v1/search"
  data = urlencode({'q': name, "type": "artist"})
  search_url=f"{url}?{data}"
  response = requests.get(search_url,headers=headers).json()["artists"]["items"][0]["id"]
  return str(response)

def getRelatedArtists(name):
  artists=[]
  apiToken=getSpotifyToken()
  id=getArtistId(name,apiToken)
  headers = {'Authorization': 'Bearer ' + apiToken}
  url = "https://api.spotify.com/v1/artists/" + id + "/related-artists"
  response=requests.get(url,headers= headers).json()
  for i in range (0, len(response['artists'])):
    artists.append(str(response['artists'][i]['name']))
  return artists


def getArtistInfo(name, page):
  url="https://api.genius.com"
  headers = {'Authorization': 'Bearer ' + configs.apiToken}
  search_url = url + '/search?per_page=10&page=' + str(page)
  data = {'q': name}
  response = requests.get(search_url, data=data, headers=headers)
  return response

def getSongUrl(name):
    page = 1
    songs = []
    
    while True:
        response = getArtistInfo(name, page)
        json = response.json()        # Collect up to song_cap song objects from artist
        songInfo = []
        for hit in json['response']['hits']:
            if name.lower() in hit['result']['primary_artist']['name'].lower():
                songInfo.append(hit)
        url=""
        for song in songInfo:
            url = song['result']['url']
            songs.append(url)
        if url == "":
          break
        else:
          page+=1
        
        
    print('Found {} songs by {}'.format(len(songs), name))
    return songs

def scrapeLyrics(name):
  songs= getSongUrl(name)
  lyrics=[]
  titles=[]
  for i in range (len(songs)):
    page = requests.get(songs[i])
    html = BeautifulSoup(page.text, 'html.parser')
    lyric="-"
    title="-"
    try:
      lyric = html.find('div', class_='lyrics').get_text()
      titleString=html.title.string
      title=re.search('%s(.*)%s' % (" – ", " Lyrics | Genius Lyrics"), titleString).group(1)
    except:
      pass
    try:
      title=title.replace("/", "-")
    except:
      pass
    lyric = re.sub(r'[\(\[].*?[\)\]]', '', lyric)
    lyric = os.linesep.join([s for s in lyric.splitlines() if s]) 
    lyrics.append(lyric)   
    titles.append(title)   
  return lyrics,titles

def createDataSet(name,filePath):
  lyrics,titles=scrapeLyrics(name)
  try:
    os.mkdir(filePath)
  except:
    pass
  filepath=filePath+name
  try:
    os.mkdir(filepath)
  except:
    pass
  for i in range(len(lyrics)):
    compPath=os.path.join(filepath, str(titles[i])+".txt")
    f=open(compPath,"w+")
    f.write(lyrics[i].lower())
    f.close
    print(titles[i])

def main():
  name = input("name of artist:")
  filePath="/content/datasets/" + name + " dataset/"
  artists=getRelatedArtists(name)
  artists.append(name)
  length = len(artists)
  for i in range (0,length-1):
    otherArtists=getRelatedArtists(artists[i])
    for artist in otherArtists:
      if artist not in artists:
        artists.append(artist)
  print(artists)
  for artist in artists:
    createDataSet(artist,filePath)

main()