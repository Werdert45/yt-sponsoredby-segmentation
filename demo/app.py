import time
from flask import Flask
from flask import request
from flask import render_template


app = Flask(__name__)


def long_load(typeback):
    time.sleep(5)
    return f"You typed: {typeback}"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def form(display=None):
    query = request.form["anything"]
    outcome = long_load(query)
    return render_template("done.html", display=outcome)


@app.route("/docs")
def docs():
    return render_template("docs.html")


@app.route("/authors")
def author():
    return render_template("author.html")


if __name__ == "__main__":
    app.debug = True
    app.run()
