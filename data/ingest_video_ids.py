import pandas as pd
from pymongo import MongoClient


conn_str = "mongodb://49.13.173.177:27020/"
client = MongoClient(conn_str)


def add_video_ids(sponsor_path):
    client = MongoClient(conn_str)
    for chunk in pd.read_csv(sponsor_path, chunksize=100000):
        df = chunk
        df['retrieved'] = 0
        dic = df[['videoID', 'startTime', 'endTime', 'votes', 'UUID', 'category', 'timeSubmitted', 'retrieved']].to_dict('records')
        client.sponsoredbye.video_id.insert_many(dic)
        print("Added a cluster")



def format_video_ids():
    client.sponsoredbye.video_id.delete_many({'votes': {"$lte": 2}})
    print(len(client.sponsoredbye.video_id.distinct("_id")))
    return True
