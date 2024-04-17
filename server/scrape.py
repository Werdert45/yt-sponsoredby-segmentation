import mysql.connector
from pymongo import MongoClient
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import json

comp_limit = 500


client = MongoClient()
db = mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="password"
        )

cursor = db.cursor(buffered=True)



def getIds():
    query = f"SELECT * FROM segmentedbye.video_ids WHERE retrieved=0 AND votes > 5 LIMIT {comp_limit}"
    cursor.execute(query)
    return cursor.fetchall()



def getBasicInformation(vid_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid_id)
    except Exception as e:
        raise e
    req = requests.get(f'https://yt.lemnoslife.com/noKey/videos?part=snippet&id={vid_id}')
    if req.status_code == 200:
        information = json.loads(req.content)
    else:
        print(req.status_code)
        information = None
        return False
    information['transcript'] = transcript
    return information


def retrieveData(obj):
    video_id = obj[0]
    try:
        information = getBasicInformation(video_id)
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

if __name__ == "__main__":
    while True:
        ids = getIds()
        print(ids[0])
        for elem in ids:
            data = retrieveData(elem)
            # Update the retrieved key in the sql
            cursor.execute(f"UPDATE segmentedbye.video_ids SET retrieved=1 WHERE videoID='{elem[0]}'")
            db.commit()
            # Add the entry to the MongoDB
            print(elem)
            if data:
                client.sponsoredbye.raw.insert_one(data)
