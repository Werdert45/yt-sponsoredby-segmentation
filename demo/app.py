import time
from flask import Flask
from flask import request
from flask import render_template


app = Flask(__name__)


def long_load(typeback):
    """
    - Validate that the url is correct
    - Get the transcript
    - Segment by sending it to the sentence segmenter
    - Process data to be send to our model
    - Run the model
    - Infer the time stamps
    """
    time.sleep(5)
    return {
        "title": "Video Title",
        "channel_name": "ChannelID",
        "timestamps": [("20:03", "21:02"), ("1:34:04", "1:34:43")],
        "video_url": "https://www.youtube.com/watch?v=4S-8mjx7qJU",
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def answer(display=None):
    query = request.form["video_url"]
    print("==============\n============")
    print(query)
    print("==============\n============")
    outcome = long_load(query)
    return render_template("result.html", display=outcome)


@app.route("/docs")
def docs():
    return render_template("docs.html")


@app.route("/authors")
def author():
    return render_template("author.html")


if __name__ == "__main__":
    app.debug = True
    app.run()
