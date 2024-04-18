from mysql.connector import connect
import datetime
import time
from tqdm import tqdm
from pymongo import MongoClient
import pandas as pd

"""
Functions included:
    - rawToData: move the raw data collected to the data directory
    - cleanDuplicatetimes: a problem that arises with times being very close to each other, remove these and keep only 1
    - removeShortTimes: remove sponsored segments of less than a certain threshold
    - addTag: add the tag to the data, to add into clean folder

"""

client = MongoClient()

def rawToData():
    unique_ids = client.sponsoredbye.raw.distinct("videoID")
    print(f"Found {len(unique_ids)} unique ids")
    added = 0
    updated = 0
    for vid_id in tqdm(unique_ids):
        sub = [x for x in client.sponsoredbye.raw.find({"videoID": vid_id})]
        data_query = client.sponsoredbye.data.find_one({"videoID": vid_id})
        if data_query:
            # There is an existing value, so check if value already incldued for start, end, if not add
            for elem in sub:
                if elem['startTime'] not in data_query['start_times']:
                    data_query['start_times'].append(elem['startTime'])
                if elem['endTime'] not in data_query['end_times']:
                    data_query['end_times'].append(elem['endTime'])

            # Update the new record
            assert data_query['start_times'] == len(data_query['end_times'])
            client.sponsoredbye.data.update_one({'_id': data_query['_id']}, 
                    {"$set": {'end_times': data_query['end_times']}, 'start_times': data_query['start_times']})

            updated += 1
        else:
            data = sub[0]

            start_times = [x['startTime'] for x in sub]
            end_times = [x['endTime'] for x in sub]
            video_id = sub[0]['videoID']
            data['start_times'] = start_times
            data['end_times'] = end_times
            # Insert the new record into the db here
            client.sponsoredbye.data.insert_one(data)
            added += 1
    print(f"Updated {updated} and added {added} from raw to data")
    return True

def removeDuplicates():
    unique_ids = client.sponsoredbye.data.distinct("videoID")
    found_ids = []
    cur_len = len(client.sponsoredbye.data.find({}).distinct("_id"))
    cursor = client.sponsoredbye.data.find({})
    for elem in tqdm(cursor, total=cur_len):
        if 'videoID' not in elem:
            client.sponsoredbye.data.delete_many({"_id": elem['_id']})
            continue
        if elem['videoID'] not in found_ids:
            found_ids.append(elem['videoID'])
        else:
            client.sponsoredbye.data.delete_one({"_id": elem['_id']})

    print(cur_len) 
    print("=>")
    print(len(client.sponsoredbye.data.find({}).distinct("_id")))
    return True


def cleanDuplicateTimes(data, threshold=30):

    duplicates = 0
    new_start = []
    start = data['start_times']
    start.sort()
    for i, elem in enumerate(start):
        if not new_start:
            new_start.append(elem)
            continue
        if new_start[-1] + threshold < elem:
            new_start.append(elem)
        else:
            duplicates += 1

    new_stop = []
    stop = data['end_times']
    stop.sort()

    for i, elem in enumerate(stop):
        if not new_stop:
            new_stop.append(elem)
            continue
        if new_stop[-1] + threshold < elem:
            new_stop.append(elem)
        else:
            duplicates += 1
    if len(new_start) != len(new_stop):
        # TODO: this is problematic and we should continue
        return None, None
    data['start_times'] = new_start
    data['end_times'] = new_stop
    # return {"start": start, "start_times": data['start_times'], "stop": stop, "end_times": data['end_times']}
    return new_start, new_stop


def removeShortTimes(data, threshold=10):
    start = data['start_times']
    end = data['end_times']

    new_start = []
    new_stop = []

    for i in range(len(start)):
        s, e = start[i], end[i]
        if s + threshold < e:
            new_start.append(s)
            new_stop.append(e)
    return new_start, new_stop



def addTag(elem, s, e):
    in_sponsor = False
    for i, sent in enumerate(elem['transcript']):
        if len(elem['transcript']) - 1 > i:
            next_sent = elem['transcript'][i+1]
        else:
            if in_sponsor:
                # Still add the close tag
                elem['transcript'][i]['text'] = elem['transcript'][i]['text'] + '</s>'
        if in_sponsor:
            # Check if the end is reached
            if e < (next_sent['start'] + next_sent['duration']):
                elem['transcript'][i]['text'] = elem['transcript'][i]['text'] + '</s>'
                break
        else:
            # Check if now in a sponsor
            if s < next_sent['start']:
                in_sponsor = True
                # Add the <s> sign
                elem['transcript'][i]['text'] = '<s>' + elem['transcript'][i]['text']
                # print(i)
    
    text = ""
    
    for sent in elem['transcript']:
        text += sent['text'] + " "
        
    elem['text'] = text
    return elem


def clean():
    # Add the raw data (on _id to distinguish)
    start = time.time()
    print(f"Started cleaning pipeline at {datetime.datetime.fromtimestamp(start).strftime('%c')}")    
    print("Adding raw collection data to data collection (or updating existing)")
    rawToData()

    print("Removing duplicates")
    removeDuplicates()

    print("Cleaning up the code")
    removed_dup = 0
    error = 0
    total = client.sponsoredbye.data.find({}).distinct("_id")
    for elem in tqdm(client.sponsoredbye.data.find({}), total=len(total)):
        old_start, old_stop = elem['start_times'], elem['end_times']
        new_start, new_stop = cleanDuplicateTimes(elem)
        if not new_start:
            error += 1
            client.sponsoredbye.data.update_one({"_id": elem['_id']}, {"$set": {'error': 1}})
            continue
        elem['start_times'], elem['end_times'] = new_start, new_stop
        new_start, new_stop = removeShortTimes(elem)
        
        if len(old_start) == len(new_start) and len(old_stop) == len(new_stop):
            continue
        else:
            removed_dup +=1
            client.sponsoredbye.data.update_one({"_id": elem['_id']}, 
                    {"$set": {'start_times': new_start, 'end_times': new_stop}})
    print(f"Muted {removed_dup} entries to remove duplicate <s> down the line, with {error} errors due to inconsistencies")


    print("Adding tags to clean collection")
    if input("Are you sure you want to remove the clean collection and update it (Y/n)?") == "Y":
        client.sponsoredbye.clean.delete_many({})
    else:
        print("Now adding on top of existing data")
    total = len(client.sponsoredbye.data.find({}).distinct("_id"))
    tag_error = 0
    for elem in tqdm(client.sponsoredbye.data.find({}), total=total):
        elem['start_times'].sort()
        elem['end_times'].sort()
        s = elem['start_times']
        e = elem['end_times']

        for s,e in list(zip(s,e)):
            try:
                elem = addTag(elem, s, e)
            except:
                tag_error += 1
        if 'text' not in elem:
            elem['text'] = ""
        if 'error' not in elem:
            elem['error'] = 0
        new = {"videoID": elem['videoID'], 'transcript': elem['transcript'], "text": elem['text'], 'start_times': elem['start_times'], 'end_times': elem['end_times'], 'title': elem['title'], 'error': elem['error']}
        client.sponsoredbye.clean.insert_one(new)
    print(f"Succesfully added {total} entries into the clean dataset at {datetime.datetime.fromtimestamp(start).strftime('%c')} there were {tag_error} errors with adding the tags")
    end = time.time()
    print(f"Whole process took {end-start} seconds.")


if __name__ == "__main__":
    clean()
