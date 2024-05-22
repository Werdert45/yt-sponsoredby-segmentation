from ingest_video_ids import format_video_ids, add_video_ids
from scrape_transcripts import scrape
from clean_data import clean
from pymongo import MongoClient
from add_punctuation import punctuate_sentences
from add_embeddings import add_embeddings

# This sponsorTimes file comes from:
sponsor_path = "../scraper/sponsorTimes.csv"

def data_pipeline(sponsor_path):
    conn_str = "mongodb://49.13.173.177:27020/"
    client = MongoClient(conn_str)

    """
    Video Id Ingestion:
    from sponsorTimes file, retrieve useful video ids
    """
    if not client.sponsoredbye.video_id.find_one({}):
        add_video_ids(sponsor_path)
        format_video_ids()

    """
    Scrape:
    - Scrape the video ids (if retrieved == 0)
    - Do this every ~5 seconds to not overload API
    """
    scrape()

    """
    Clean:
    - move raw collection data to data
    - Remove duplicates from the data collection
    - Remove short times, that have to be wrong data
    - Add tags for where the sponsored segments are
    - Finally move to clean collection
    - In the clean collection, add punctuation for the transcripts without them
    """
    clean()
    punctuate_sentences()

    """
    Embeddings:
    - To make training easier, where no transformer model has to be loaded in
    - Stored in sponsoredbye.embeddings column
    """
    add_embeddings()

    print("Sucessfully processed data")
