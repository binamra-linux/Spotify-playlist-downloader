from dotenv import load_dotenv
import os
import requests
import json
import re
import yt_dlp as ydl
# https://open.spotify.com/playlist/62Te6gAHes0XHKG8voniR8?si=212ad07a636d47e5  
# https://open.spotify.com/playlist/1krlRZNqDmANljqZsJXf2G?si=5e76af4f0bad4a61
load_dotenv()

# Integrating client id and client secret in the code
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")



# This function fetches access token for the spotify
def get_token():
    auth_url = "https://accounts.spotify.com/api/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded'
    }
    auth_response = requests.post(auth_url, data=data, headers=headers)
    json_result = json.loads(auth_response.content)
    token = json_result["access_token"]
    return token


# Setting authorization headers for easier future use.
# Need to send with every request
def auth_header(token):
    return {"Authorization": "Bearer " + token}



def get_playlist(token, playlist_id):
    url = "https://api.spotify.com/v1/playlists/"+playlist_id+"/tracks"
    headers = auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    num = json.loads(result.content)["total"]#["items"][1]["track"]["name"]
    songsWithArtist = []
    for i in range(0, num):
        artistName = json.loads(result.content)["items"][i]["track"]["artists"]
        songName = json_result["items"][i]["track"]["name"]
        for j in artistName:
            singer = j["name"]
            musicDetail = singer+" "+songName
            songsWithArtist.append(musicDetail)
    
    return songsWithArtist
# Get links of songs from spotify in youtube
def getLinks(songs):
    Ylinks = []
    for i in songs:
        url = f"https://www.youtube.com/results?search_query={i}"
        res = requests.get(url)
        data = res.text
        search_results = re.findall(r"watch\?v=(\S{11})", data)
        first_vid = "https://www.youtube.com/watch?v=" + search_results[0]
        Ylinks.append(first_vid)
    return Ylinks

def download_audio(output_path, Links, ffLo):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffLo
    }
    for i in Links:
        with ydl.YoutubeDL(ydl_opts) as yd:
            yd.download([i])




username = os.getlogin()

output_directory = f"C:\\Users\\{username}\\Downloads"




playlist_url = input("Enter Playlist URL:- ")
match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url)

playlist_id = match.group(1)

token = get_token()
songs = get_playlist(token, playlist_id) # returned value of the function is stored in songs variable
Links = getLinks(songs)
currentDir = os.getcwd()
ffLo = currentDir+r"\ffmpeg\bin"
download_audio(output_directory, Links, ffLo)


