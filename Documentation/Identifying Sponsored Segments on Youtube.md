# Research Proposal: *Identifying Sponsored Segments on Youtube*

## Introduction
Over the course of the years, youtube videos have included more and more brand deals in their videos. This is in part due to the Youtube Adpocalypse, which forced youtubers to find alternative ways to get paid. This in addition with brands discovering that sponsering and advertising in this fashion is a proven method of creating brand recognition. This change however comes with a decrease in viewer enjoyment as the user has probably already seen the ads that are displayed and needs to watch a 30 second to a minute ad. This combined with the sometimes two unskippable ads, makes watching youtube videos an unpleasant experience, where the watcher has to watch an average of 2 minutes of ads for a 10 minute video. Can we change this? Although adblocker or simply purschasing a youtube premium subscription removes the unskipable ads, the sponsored part of the video cannot be omitted in such a fashion. This paper tries to find a solution to this problem, by identifying the part of the video that is sponsored, segmenting this and returning a confidence score about this certain part being an ad. This will in turn allow the viewer to skip this part, using either a button or scrolling by himself. During this research, a plethora of different algorithms will be used, with tf-idf as the baseline model. The research question for this paper will thus be: *Is it possible to accurately predict the sponsored section in Youtube videos, using nlp algorithms?*. We hypothesize that this will be possible, using a manually labeled dataset of youtube video transcripts. 

## Method
This project is divided into four steps: dataset collection, model training, model evaluation and implementing in a Chrome extention. All of these steps are summarized down below:

#### 1. Dataset collection
To collect the dataset, the python library `youtube-transcript-api` is used. This api allows us to get the transcript data of the video in text format, so that we can then annotate this data. To start off, the data is annotated, using `<s></s>` tags, which surround the sponsored by section. This segmentation, later allows to implement it into any of the models. 

#### 2. Model Training
For the models, the baseline is the tf-idf algorithm, which uses document similarity to find corresponding documents and can thus categorize different windows. The algorithms that are tested against this baseline are:

- word2vec
- BERT/TinyBERT
- LSTMs
- LCSeg (Unsupervised)


All of these algorithms will be measured in different types of metrics in the next part.


#### 3. Model evaluation
For the model evaluation, the most important metric is accuracy and recall. Because the golden values that are given to the dataset are not 100% true in some cases, a precision score is also required, which instead of looking at the performance of finding the exact word, gives a performance score based on a certain window around the true label. Take the following example:

> \<s> That brings us to the sponsor of today's video

For example if the segmentation should have been before That, but the model predicts sponsor, a different metric will indicate a score rating, which is then also taken into account. We can tweak with these hyperparameters (in this case the window size parameter), to get a satisfactory score. Other metrics that are often used in text segmentation are the WindowDiff or Pk score[2], which we can also use, instead of creating a custom version. 

#### 4. Creating a Google Chrome Extension
Now that we have found the best model for creating a light weight model, we can create a chrome extension that queries the youtube transcripts and returns the segmented part. This in turn also needs to use Text to Speech and see the real timestamps. This is not part of the research itself, but of the creation of the product. The creation of the extension itself is not that complex[4].


## Sources
- [[1] Scraping NLP Datasets from Google - Hackernoon](https://hackernoon.com/how-to-scrape-nlp-datasets-from-youtube)
- [[2] Text Segmentation Approaches - AssemblyAI](https://www.assemblyai.com/blog/text-segmentation-approaches-datasets-and-evaluation-metrics/)
- [[3] TinyBERT - Github](https://github.com/yinmingjun/TinyBERT)
- [[4] Building a Chrome Extension - FreeCodeCamp](https://www.freecodecamp.org/news/building-chrome-extension/)