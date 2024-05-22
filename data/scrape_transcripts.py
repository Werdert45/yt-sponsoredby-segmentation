from pymongo import MongoClient
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import json
import time


conn_str = "mongodb://49.13.173.177:27020/"

def get_transcript(vid_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid_id)
    except Exception as e:
        return False
    req = requests.get(f'https://yt.lemnoslife.com/noKey/videos?part=snippet&id={vid_id}')
    if req.status_code == 200:
        information = json.loads(req.content)
    else:
        print(req.status_code)
        information = None
        return False
    information['transcript'] = transcript
    return transcript


def retrieveData(obj):
    video_id = obj[0]
    try:
        information = get_transcript(video_id)
    except Exception as e:
        print(e)
        return False
    if not information:
        return False
    val_dict = {'source': information}
    try:
        val_dict['title'] = information['items'][0]['snippet']['title']
    except:
        pass
    try:
        val_dict['description'] = information['items'][0]['snippet']['description']
    except:
        pass
    try:
        val_dict['tags'] = information['items'][0]['snippet']['tags']
    except:
        pass
    try:
        val_dict['transcript'] = information['transcript']
    except:
        pass
    val_dict['retrieved'] = 1
    val_dict['videoID'] = video_id

    return val_dict


def scrape():
    client = MongoClient(conn_str)
    cursor = client.sponsoredbye.video_id.find({'retrieved': 0})
    for video_id in cursor:
        data = retrieveData(video_id['videoID'])
        if data:
            client.sponsoredbye.raw.insert_one(data)
        client.sponsoredbye.video_id.update_one({"_id": video_id['_id']}, {"$set": {'retrieved': 1}})
        time.sleep(3)

