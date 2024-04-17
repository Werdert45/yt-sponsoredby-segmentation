# YouTube Sponsored By Segment Classification


## Introduction
This project aims to segment the sponsored by segments in youtube videos, to give the user only the contents of the video that he/she wants.


## Data Collection
Data is collected using the YoutubeLemmo 'Fake' YouTube API to collect data. This data is then processed by the datapipeline to be cleaned and processed. Data is collected and then annotated with <s> tags to indicate where the add is.


## Model



> NOTE: I think it is important to connect all of the text together into one document. This makes it so that there is no distinction between starting/ending of video, as there is no data without ads. The sentences consequently are the input. An alternative is using paragraphs.
