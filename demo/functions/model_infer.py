from keras.preprocessing.sequence import pad_sequences
import numpy as np
import re

# import tensorflow as tf
import os
import requests
from keras.models import load_model

headers = {"Authorization": f"Bearer {os.environ['HF_Token']}"}

model = load_model("./RNN_model.keras")


def query_embeddings(texts):
    payload = {"inputs": texts, "options": {"wait_for_model": True}}

    model_id = "sentence-transformers/sentence-t5-base"
    API_URL = (
        f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    )
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def preprocess(sentences):
    max_len = 1682
    embeddings = query_embeddings(sentences)

    if len(sentences) > max_len:
        X = embeddings[:max_len]
    else:
        X = embeddings
    X_padded = pad_sequences([X], maxlen=max_len, dtype="float32", padding="post")
    return X_padded


def predict_from_document(sentences):
    preprop = preprocess(sentences)
    prediction = model.predict(preprop)
    # Set the prediction threshold to 0.8 instead of 0.5, now use mean
    if np.mean(prediction) < 0.5:
        output = (prediction.flatten()[: len(sentences)] >= 0.5).astype(int)
    else:
        output = (
            prediction.flatten()[: len(sentences)]
            >= np.mean(prediction) * 1.20  # + np.std(prediction)
        ).astype(int)
    return output, prediction.flatten()[: len(sentences)]
