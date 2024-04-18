import pandas as pd
from urllib.request import urlretrieve
import os
import requests


def download_data(file_name="data.json"):
    retrieved = False
    if file_name in os.listdir():
        local = os.path.getsize(file_name)
        req = requests.get("http://49.13.173.177/file_size")
        content = eval(req.content.decode("utf-8"))
        remote = content["size"]
        if local == remote:
            retrieved = True
        else:
            retrieved = False

    if not retrieved:
        print("File not found, downloading now")
        url = "http://49.13.173.177/data/data.json"
        urlretrieve(url, file_name)
    else:
        print("File already found in directory")
    return True
