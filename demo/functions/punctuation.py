import requests
from youtube_transcript_api import YouTubeTranscriptApi
import json
import os

headers = {
    "Authorization": f"Bearer {os.environ['HF_Token']}"
}  # NOTE: put this somewhere else


def retrieve_transcript(vid_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid_id)
        return transcript
    except Exception as e:
        return None


def split_transcript(transcript, chunk_size=40):
    sentences = []
    for i in range(0, len(transcript), chunk_size):
        to_add = [x["text"] for x in transcript[i : i + chunk_size]]
        sentences.append(" ".join(to_add))
    return sentences


def query_punctuation(splits):
    payload = {"inputs": splits}
    API_URL = "https://api-inference.huggingface.co/models/oliverguhr/fullstop-punctuation-multilang-large"
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def parse_output(output, comb):
    total = []

    # loop over the response from the huggingface api
    for i, o in enumerate(output):
        added = 0
        tt = comb[i]
        for elem in o:
            # Loop over the output chunks and add the . and ?
            if elem["entity_group"] not in ["0", ",", ""]:
                split = elem["end"] + added
                tt = tt[:split] + elem["entity_group"] + tt[split:]
                added += 1
        total.append(tt)
    return " ".join(total)


def punctuate(video_id):
    transcript = retrieve_transcript(video_id)
    splits = split_transcript(
        transcript
    )  # Get the transcript from the YoutubeTranscriptApi
    resp = query_punctuation(splits)  # Get the response from the Inference API
    punctuated_transcript = parse_output(resp, splits)
    return punctuated_transcript, transcript
