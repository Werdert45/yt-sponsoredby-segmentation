import pandas as pd
import re 
from tqdm import tqdm
import argparse

### how to run example
### python3 labeling.py --input_file /Users/deryadurmush/Documents/DSBA/NLP_course/Project/data.json.2 --output_directory /Users/deryadurmush/Documents/DSBA/NLP_course/Project/processed --batch_size 100000 --chunk_size 150

### function to make batces later
def split_text_into_chunks(text, chunk_size=150):
    words = text.split()
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

### function for labeling one batch
def stupid_labeling(data):
    data['adv'] = 0
    for i, chunk in enumerate(data['chunk']):
            if '<s>' in chunk:
                data.loc[i, 'adv'] = 1
                if '</s>' not in chunk and i+1 < len(data['chunk']):
                    j = i+1
                    while j < len(data['chunk']) and '</s>' not in data['chunk'][j]:
                        data.loc[j, 'adv'] = 1
                        j += 1
                    if j < len(data['chunk']):
                        data.loc[j, 'adv'] = 1
    return data 

### function to clean from tags
def clean_from_tags(data):
    data['chunk'] = data['chunk'].apply(lambda x: re.sub(r'<\/?s>', '', x))
    return data


def process_df_in_batches(df, output_dir,  batch_size=10000, chunk_size=150):
    for batch_index in tqdm(range(0, len(df), batch_size)):
        batch_df = df.iloc[batch_index:batch_index+batch_size]
        data_list = []
        for i in range(len(batch_df)):
            text = batch_df['text'].iloc[i]
            chunks = split_text_into_chunks(text, chunk_size)
            for chunk in chunks:
                data_list.append({'videoID': batch_df['videoID'].iloc[i], 'chunk': chunk})
        
        batch_processed_df = stupid_labeling(pd.DataFrame(data_list))
        batch_processed_df = clean_from_tags(batch_processed_df)        

        output_filename = f"{output_dir}/batch_{batch_index//batch_size}.csv"
        batch_processed_df.to_csv(output_filename, index=False)


def main(args):
    df = pd.read_json(args.input_file, lines=True)
    process_df_in_batches(df, args.output_directory, args.batch_size, args.chunk_size)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process data in batches')
    parser.add_argument('--input_file', type=str, help='Path to input CSV file')
    parser.add_argument('--output_directory', type=str, help='Directory to save output CSV files')
    parser.add_argument('--batch_size', type=int, default=10000, help='Batch size for processing data')
    parser.add_argument('--chunk_size', type=int, default=150, help='Chunk size for splitting text into chunks')
    args = parser.parse_args()
    main(args)