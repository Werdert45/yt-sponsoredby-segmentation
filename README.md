# YouTube Sponsored By Segment Classification


## Introduction
This project aims to segment the sponsored by segments in youtube videos, to give the user only the contents of the video that he/she wants. A full description of the project can be found in the directory paper.


## Data Collection
Data is collected using the YoutubeLemmo 'Fake' YouTube API to collect data. This data is then processed by the datapipeline to be cleaned and processed. Data is collected and then annotated with \<s\> tags to indicate where the add is.


## Model
The model uses a T5-embedding, Bidirectional LSTM structure that outputs probabilities for the different sentences.


## Evaluation
Evaluation is done with f1 scores, WindowDiff and Pk score. 


## Data 
To get access to the Mongo containing the data, please contact ian.ronk0@gmail.com. A sample can be found in `data/data_sample.json`
