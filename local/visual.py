import pandas as pd
from urllib.request import urlretrieve
import os
import requests
from collections import Counter
import re
import matplotlib.pyplot as plt
import numpy as np
import time


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



def check_unique(df):
    '''
    Check if all videoID are unique
    '''
    videoID = list(df['videoID'])
    element_counts = Counter(videoID)
    non_unique_elements = [element for element, count in element_counts.items() if count > 1]
    print(f'There are {len(non_unique_elements)} not unique elements')

def adv_texts(df):
    '''
    Extract the text between the <s> and </s> tags and create a new DataFrame with the videoID and the extracted text
    '''
    data_list = []
    for i in range(len(df)):
        text = df['text'][i]
        pattern = r'<s>(.*?)</s>'
        matches = re.findall(pattern, text)
        for match in matches:
            data_list.append({'videoID': df['videoID'][i], 'text': match})
    adv = pd.DataFrame(data_list)
    adv['word_count'] = adv['text'].apply(lambda x: len(x.split()))
    return adv   


def word_count_graph(df, restrict_length=False, max_length=None, name='word_count.png'):
    '''
    Create a histogram of the word count of the text column
    
    Parameters:
        - df: DataFrame containing the text column
        - restrict_length: Boolean indicating whether to restrict the word count length (default: True)
        - max_length: Maximum length to restrict the word count (default: None)
    '''
    if restrict_length:
        df['word_count'] = df['text'].apply(lambda x: len(x.split()))
        df = df[df['word_count']>0]
        print('Excluded', len(df[df['word_count'] > max_length]), 'videos with more than', max_length, 'words.')
        df = df[df['word_count'] <= max_length]

    else:
        df['word_count'] = df['text'].apply(lambda x: len(x.split()))
    
    plt.hist(df['word_count'], bins=20, color='skyblue', edgecolor='black')
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Distribution of word count per video')
    plt.savefig(name)
    plt.close()

def adv_per_video(df, name='adv_per_video.png'):
    '''
    Create a DataFrame with the number of ads per video
    '''
    adv_per_video = df.groupby('videoID').size()
    plt.hist(adv_per_video, bins=20, color='skyblue', edgecolor='black')
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Distribution of number of advertisments per video')
    plt.savefig(name)
    plt.close()

def bin_ranges(df):
    '''
    Create a DataFrame with the bin ranges and the percentage in each bin
    '''
    bin_counts, bins = np.histogram(df['word_count'], bins=20)

    total_points = len(df)
    percentages = bin_counts / total_points * 100

    data = {'Bin Range': [], 'Percentage': []}
    for i in range(len(bins) - 1):
        range_str = f'{bins[i]:.2f} - {bins[i+1]:.2f}'
        data['Bin Range'].append(range_str)
        data['Percentage'].append(percentages[i])

    ranges_and_percentages_df = pd.DataFrame(data)
    print(ranges_and_percentages_df)
    return ranges_and_percentages_df

def main():
    t = time.time()
    df = pd.read_json('data.json.1', lines=True)
    print('Time taken to read the json file:', time.time()-t)
    check_unique(df)
    ## distributions for whole videos 
    word_count_graph(df, restrict_length=False, name ='video_word_count_unrestricted.png')
    word_count_graph(df, restrict_length=True, max_length=10000, name = 'video_word_count_max_10000.png')
    print('Bin ranges for whole videos')
    bin_ranges(df)
    ## ads per video
    adv = adv_texts(df)
    adv_per_video(adv)
    ## distributions for ads
    word_count_graph(adv, restrict_length=False, name ='adv_word_count_unrestricted.png')
    word_count_graph(adv, restrict_length=True, max_length=1000, name = 'adv_word_count_max_1000.png')
    print('Bin ranges for ads')
    bin_ranges(adv)

if __name__ == "__main__":
    main()

