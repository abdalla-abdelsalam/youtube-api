  
import os
import re
from datetime import timedelta
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pathlib import Path
import pprint

# load the environment varibles
def load_env():
    env_path=Path('.')/'.env'
    load_dotenv(dotenv_path=env_path)

# parsing the playlist link to get playlist id
def playlist_link():
    try:
        playlist_link=input("please enter playlist link: ")
        txt=r'playlist\?list=.*'
        playlist_id_pattern= re.search(txt, playlist_link)
        _,id=playlist_id_pattern.group(0).split('=')
    except AttributeError:
        print("invalid playlist link")
        exit()
    else:
        return id
    

def time_process(total_seconds):
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return hours,minutes,seconds



'''
connecting to youtube api to get playlist videos id and go through each one of them to get the duration 
of that video then get the total duration of the playlist by by summing all the durations together
''' 
def youtube_api_playlistItems():
    api_key = os.environ.get('API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)
    nextPageToken = None
    hours_pattern = re.compile(r'(\d+)H')
    minutes_pattern = re.compile(r'(\d+)M')
    seconds_pattern = re.compile(r'(\d+)S')
    total_seconds = 0
    while True:
        pl_request = youtube.playlistItems().list(
            part=['contentDetails'],
            playlistId="PL-osiE80TeTsWmV9i9c58mdDCSskIFdDS",
            maxResults=50,
            pageToken=nextPageToken
        )

        pl_response = pl_request.execute()

        vid_ids = []
        for item in pl_response['items']:
            vid_ids.append(item['contentDetails']['videoId'])

        vid_request = youtube.videos().list(
            part="contentDetails",
            id=','.join(vid_ids) 
        )
        vid_response = vid_request.execute()
        # looping through each vidoe to get its duration time
        for item in vid_response['items']:
            duration = item['contentDetails']['duration']

            hours = hours_pattern.search(duration)
            minutes = minutes_pattern.search(duration)
            seconds = seconds_pattern.search(duration)

            hours = int(hours.group(1)) if hours else 0
            minutes = int(minutes.group(1)) if minutes else 0
            seconds = int(seconds.group(1)) if seconds else 0

            video_seconds = timedelta(
                hours=hours,
                minutes=minutes,
                seconds=seconds
            ).total_seconds()

            total_seconds += video_seconds

        nextPageToken = pl_response.get('nextPageToken')

        if not nextPageToken:
            break
    return int(total_seconds)



def output_format(hours,minutes,seconds):
    print(f'playlist time duration: {hours}h:{minutes}m:{seconds}s')


if __name__=="__main__":
    load_env()
    id=playlist_link()
    total_seconds=youtube_api_playlistItems()
    hours,minutes,seconds=time_process(total_seconds)
    output_format(hours,minutes,seconds)

