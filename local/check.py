#!/bin/bash

#SBATCH --account=3214046
#SBATCH --partition=dsba
#SBATCH --gpus=1
#SBATCH --mem=10G
#SBATCH --job-name="check of db" 
#SBATCH --time=00:01:00
#SBATCH --output=/home/3214046/my_dir/output/%x.out
#SBATCH --error=/home/3214046/my_dir/error/%x.err

import pandas as pd
import re
from deepmultilingualpunctuation import PunctuationModel
from tqdm import tqdm

def split_text_into_sentences(text):
    pattern = r'(?<=[.!?…]) +' 
    sentences = re.split(pattern, text)
    return sentences

def sentence_split(df):
    data_list = []
    for i in range(len(df)):
        text = df['text'].iloc[i]
        sent = split_text_into_sentences(text)
        for s in sent:
            data_list.append({'videoID': df['videoID'].iloc[i], 'sentence': s})
    res = pd.DataFrame(data_list)
    return res

def main():
    # Load the data
    print("Loading data...")
    df = pd.read_json('data.json', lines=True, nrows=10000)
    print(f"Number of videos: {len(df)}")
    
    # Filter out empty texts
    df['word_count'] = df['text'].apply(lambda x: len(x.split()))
    df = df[df['word_count'] > 0]
    df = df.reset_index(drop=True)
    print(f"Number of videos with text: {len(df)}")
    
    # Make a new dataframe with each sentence as a row
    sent_df = sentence_split(df)
    sent_df.to_csv('sentences_10000.csv', index=False)
    print(f"Number of sentences: {len(sent_df)}")
    
    # Filter the DataFrame to include only videos with one sentence
    sent_per_video = sent_df.groupby('videoID').count()
    videos_with_one_sentence = sent_per_video[sent_per_video['sentence'] == 1].index
    print(f"Number of videos with one 'sentence': {len(videos_with_one_sentence)}")
    
    # Apply restoration of punctuation to videos with one sentence
    model = PunctuationModel()
    videos_to_process = df[df['videoID'].isin(videos_with_one_sentence)]
    videos_to_process = videos_to_process.reset_index(drop=True)

    for i, row in tqdm(videos_to_process.iterrows(), total=len(videos_to_process), desc="Processing '1 sentence' videos"):
        videos_to_process.loc[i, 'text'] = model.restore_punctuation(row['text'])
    
    # Split the text into sentences again
    sent_df2 = sentence_split(videos_to_process)
    sent_df2.to_csv('sentences2_10000.csv', index=False)

if __name__ == "__main__":
    main()