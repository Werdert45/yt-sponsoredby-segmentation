from pymongo import MongoClient
import re
from deepmultilingualpunctuation import PunctuationModel
from tqdm import tqdm

client = MongoClient("mongodb://49.13.173.177:27020/")

def check_sentence(corpus):
    end_of_word_tags = re.findall(r'[\.\,\?]', corpus)
    metric = len(end_of_word_tags)/len(corpus.split(" "))
    if metric > 0.05:
        return True
    else:
        return False

def run_model(obj, model):
    corpus = obj['text']
    is_sentence = check_sentence(corpus)
    if is_sentence:
        client.sponsoredbye.clean.update_one({"_id": obj['_id']}, {"$set": {'retrieved': 1, 'cleaned_text': corpus}})
    else:
        new_corpus = model.restore_punctuation(corpus)
        client.sponsoredbye.clean.update_one({"_id": obj['_id']}, {"$set": {'retrieved': 1, 'cleaned_text': new_corpus}})


def punctuate_sentences():
    model = PunctuationModel()
    counter = 0
    cursor = client.sponsoredbye.clean.find({"retrieved": 0})
    for elem in tqdm(cursor):
        try:
            run_model(elem, model)
        except:
            continue
        counter += 1
        if counter % 100 == 0:
            print(f"Updated Entry {counter}")

