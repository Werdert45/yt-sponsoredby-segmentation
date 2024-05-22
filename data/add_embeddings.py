from sentence_transformers import SentenceTransformer
import re
from tqdm import tqdm
from pymongo import MongoClient

client = MongoClient("mongodb://49.13.173.177:27020/")

print("Starting Run, after loading in everything")
print("Loading in Model")
model = SentenceTransformer('sentence-transformers/sentence-t5-base')

def convert_list_to_float(lst):
    return [x.item() for x in lst]


def split_sentences(corpus):
    # Corpus is the clean corpus with sentences
    sents = re.split(r'[\.\!\?]\s', corpus.replace("<s>", "").replace("</s>", ""))
    if len(sents) < 5:
        # There are less than 5 sentences, so there is a problem
        return False
    return sents


def encode_and_store_video(obj):
    if 'cleaned_text' not in obj:
        return False
    if not obj['cleaned_text']:
        return False
    sentences = split_sentences(obj['cleaned_text'])
    if not sentences:
        print("Error in split_sentences")
        return False
    embeddings = model.encode(sentences)
    embedded_list = [{"text": sent, "embedding": convert_list_to_float(embedding)} for sent, embedding in zip(sentences, embeddings)]
#     embedded_list = [format_mongo(r) for r in embedded_list]
    if len(embeddings) > 0:
        client.sponsoredbye.embeddings.insert_one({"embeddings": embedded_list,
            "videoID": obj['videoID'],
            "start_times": obj['start_times'],
            "end_times": obj['end_times']})
        client.sponsoredbye.clean.update_one({"_id": obj['_id']},
                {"$set": {"embedded": 1}})
        return True
    else:
        client.sponsoredbye.clean.update_one({"_id": obj['_id']},
                {"$set": {"embedded_issue": 1, 'embedded': 1}})

        return False


def add_embeddings():
    cursor = client.sponsoredbye.clean.find({"embedded": 0, 'retrieved': 1}, {'cleaned_text': 1, 'embedded': 1, 'videoID': 1,
        'start_times': 1, 'end_times': 1
        })
    for obj in cursor:
        try:
            encode_and_store_video(obj)
        except:
            continue
