from pymongo import MongoClient


def set_retrieved():
    vid_ids = client.sponsoredbye.data.distinct("videoID")
    client.sponsoredbye.video_id.update_many({"videoID": {"$in": vid_ids}}, {"$set": {'retrieved': 1}})
    print(f"Not retrieved: {len(client.sponsoredbye.video_id.find({'retrieved': 0}).distinct('videoID'))}")
    return True