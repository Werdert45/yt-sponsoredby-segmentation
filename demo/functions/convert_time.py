import re
from thefuzz import fuzz
import numpy as np


def match_mask_and_transcript(split_punct, transcript, classification):
    """
    Input:
        split_punct: the punctuated text, split on ?/!/.\s,
        transcript: original transcript with timestamps
        classification: classification object (list of numbers 0,1)
    Output: times
    """

    # Get the sponsored part
    sponsored_segment = []
    for i, val in enumerate(classification):
        if val == 1:
            sponsored_segment.append(split_punct[i])

    segment = " ".join(sponsored_segment)
    sim_scores = list()

    # Check the similarity scores between the sponsored part and the transcript parts
    for elem in transcript:
        sim_scores.append(fuzz.partial_ratio(segment, elem["text"]))

    # Get the scores and check if they are above mean + 2*stdev
    scores = np.array(sim_scores)
    timestamp_mask = (scores > np.mean(scores) + np.std(scores) * 2).astype(int)
    timestamps = [
        (transcript[i]["start"], transcript[i]["duration"])
        for i, elem in enumerate(timestamp_mask)
        if elem == 1
    ]

    # Get the timestamp segments
    times = []
    current = -1
    current_time = 0
    for elem in timestamps:
        # Threshold of 5 to see if it is a jump to another segment (also to make sure smaller segments are added together
        if elem[0] > (current_time + 15):
            current += 1
            times.append((elem[0], elem[0] + elem[1]))
            current_time = elem[0] + elem[1]
        else:
            times[current] = (times[current][0], elem[0] + elem[1])
            current_time = elem[0] + elem[1]

    return_times = [x for x in times if (x[1] - x[0]) > 10]
    return return_times, timestamps
