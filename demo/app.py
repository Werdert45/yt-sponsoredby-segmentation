from os import pipe
import re
import gradio as gr
from functions.punctuation import punctuate
from functions.model_infer import predict_from_document
from functions.convert_time import match_mask_and_transcript


title = "sponsoredBye - never listen to sponsors again"
description = "Sponsored sections in videos are annoying and take up a lot of time. Improve your YouTube watching experience, by filling in the youtube url and figure out what segments to skip."
article = "Check out [the original Rick and Morty Bot](https://huggingface.co/spaces/kingabzpro/Rick_and_Morty_Bot) that this demo is based off of."


def pipeline(video_url):
    video_id = video_url.split("?v=")[-1]
    punctuated_text, transcript = punctuate(video_id)
    sentences = re.split(r"[\.\!\?]\s", punctuated_text)
    classification, probs = predict_from_document(sentences)
    #    return punctuated_text
    times, timestamps = match_mask_and_transcript(sentences, transcript, classification)
    return [{"begin": time[0], "end": time[1]} for time in times]
    #    return [
    #        {
    #            "start": "12:05",
    #            "end": "12:52",
    #            "classification": str(classification),
    #            "probabilities": probs,
    #            "times": times,
    #            "timestamps": timestamps,
    #        }
    #    ]


# print(pipeline("VL5M5ZihJK4"))
demo = gr.Interface(
    fn=pipeline,
    title=title,
    description=description,
    inputs="text",
    #    outputs=gr.Label(num_top_classes=3),
    outputs="json",
    examples=[
        "https://www.youtube.com/watch?v=UjtOGPJ0URM",
        "https://www.youtube.com/watch?v=TrZyuCh9df0",
    ],
)
demo.launch(share=True)
