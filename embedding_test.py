import requests
import os


model_id = "sentence-transformers/sentence-t5-base"

api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
headers = {"Authorization": f"Bearer {os.environ['Hugging_key']}"}


def query(texts):
    response = requests.post(
        api_url,
        headers=headers,
        json={"inputs": texts, "options": {"wait_for_model": True}},
    )
    return response.json()
