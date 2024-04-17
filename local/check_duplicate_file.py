import os
import requests


def compare_size(file_path):
    local = os.path.checksize(file_path) 
    req = requests.get("http://49.13.173.177/file_size")
    content = eval(req.content.decode("utf-8"))
    remote = content['size']
    if local == remote:
        return True
    else:
        return False
