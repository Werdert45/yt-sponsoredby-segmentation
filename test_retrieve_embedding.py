import json
from pymongo import MongoClient

client = MongoClient("mongodb://49.13.173.177:27020/")

cursor = client.sponsoredbye.embeddings.find({"embeddings.added_label": 1})


data = []

for i, elem in enumerate(cursor):
    if i == 5:
        break
    data.append(elem)

for elem in data:
    elem.pop("_id")


# Now store the data into a json to be used later
json_string = json.dumps(data)


file = open("data.json", "w")
file.write(json_string)
file.close()
