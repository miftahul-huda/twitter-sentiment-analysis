import os
import flask
import base64
import random
import string
import subprocess
import signal
import json
import thread
import copy
from subprocess import PIPE
from flask import render_template
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

from flask import request, jsonify
import requests

from google.cloud import language_v1
from google.cloud.language_v1 import enums
import sys


app = flask.Flask(__name__)
app.config["DEBUG"] = True

host = '0.0.0.0'
port = 5050

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def analyze_sentiment(text_content, lang):
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """

    client = language_v1.LanguageServiceClient()

    # text_content = 'I am so happy and joyful.'

    # Available types: PLAIN_TEXT, HTML
    type_ = enums.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = lang
    document = {"content": text_content, "type": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = enums.EncodingType.UTF8

    response = client.analyze_sentiment(document, encoding_type=encoding_type)
    # Get overall sentiment of the input document
    print(u"Document sentiment score: {}".format(response.document_sentiment.score))
    print(
        u"Document sentiment magnitude: {}".format(
            response.document_sentiment.magnitude
        )
    )
    # Get sentiment for all sentences in the document
    for sentence in response.sentences:
        print(u"Sentence text: {}".format(sentence.text.content))
        print(u"Sentence sentiment score: {}".format(sentence.sentiment.score))
        print(u"Sentence sentiment magnitude: {}".format(sentence.sentiment.magnitude))

    # Get the language of the text, which will be the same as
    # the language specified in the request or, if not specified,
    # the automatically-detected language.
    print(u"Language of the text: {}".format(response.language))
    return   response.document_sentiment.score, response.document_sentiment.magnitude 

@app.route('/', methods=['GET'])
def hello():
    return "Hello World"

@app.route('/web')
def static_file():
    return render_template('index.html')


@app.route('/search/<keyword>')
def search(keyword):
    url = "https://api.twitter.com/2/tweets/search/recent?query=" + keyword + "&expansions=author_id&tweet.fields=created_at"
    response = requests.get(url, headers={  "Authorization" : "Bearer AAAAAAAAAAAAAAAAAAAAAAfdIAEAAAAAg6rzW7QKYssOEIQjVdW2VtxAKdA%3D03VwceBCelsHUamz8gLNpLBdhUjq3C7qK6AGH0GpPPsyipRJ6j" })
    return response.json()

@app.route('/analyse/<lang>', methods=['POST'])
def analyse(lang):
    tweets = request.get_json();
    #tweets = json.loads(sjson)
    results = []
    i = 0
    try:
        for  tweet in tweets:
            text = tweet['text']
            score, magnitude = analyze_sentiment(text,  lang)
            tweet["score"] = score
            tweet["magnitude"] = magnitude
            tweet["result"] = ""
            results.append(tweet)
            i = i + 1

        return json.dumps(tweets)
    except Exception, e:
        print(e)
        return "No data  to analyse"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET','POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['uploaded_file']
      f.save(secure_filename(f.filename))
      return 'file uploaded successfully'



app.config['UPLOAD_FOLDER']  = UPLOAD_FOLDER

print("Running sentiment analysis server on " + host + ":"  + str(port))
app.run(host, port)
