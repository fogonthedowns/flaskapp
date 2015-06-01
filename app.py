#!/usr/bin/env python
from flask import Flask, url_for, jsonify
app = Flask(__name__)
import nltk, re, json, sys, logging

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route('/')
def api_root():
    return 'Welcome'

@app.route('/articles')
def api_articles():
    return 'List of ' + url_for('api_articles')

@app.route('/articles/<articleid>')
def api_article(articleid):
    return 'You are reading ' + articleid


from flask import request

@app.route('/nlp')
def api_hello():
    if 'text' in request.args:
        processed_text = ie_preprocess(request.args['text'])
        dictionary = tree_to_dict(processed_text)
        resp = jsonify(**dictionary)
        return resp
    else:
        return 'invalid'

@app.route('/echo', methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def api_echo():
    if request.method == 'GET':
        return "ECHO: GET\n"

    elif request.method == 'POST':
        return "ECHO: POST\n"

    elif request.method == 'PATCH':
        return "ECHO: PACTH\n"

    elif request.method == 'PUT':
        return "ECHO: PUT\n"

    elif request.method == 'DELETE':
        return "ECHO: DELETE"

from flask import json

@app.route('/messages', methods = ['POST'])
def api_message():

    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        return "JSON Message: " + json.dumps(request.json)

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "Binary message written!"

    else:
        return "415 Unsupported Media Type ;)"

def ie_preprocess(text):
    # timex.tag(text)
    nltk.data.path.append('./nltk_data/')  # set the path
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    
    # tag pattern - a sequence of part-of-speech tags delimited to regular expression patterns
    grammar = "NP: {<NN.*>*}"
    grammar = "NP: {<CD>*<NN.*>*}"
    cp = nltk.RegexpParser(grammar)
    result = cp.parse(sentences[0])
    #result.draw()
    ne = nltk.ne_chunk(sentences[0])
    #print result
    #print ne
    return ne

def tree_to_dict(tree):
    tdict = {}
    for t in tree:
        if isinstance(t, nltk.Tree) and isinstance(t[0], nltk.Tree):
            tdict[t.label()] = tree_to_dict(t)
        elif isinstance(t, nltk.Tree):
            if (len(t) >= 2):
                tdict[t.label()] = t[0][0] + ' ' + t[1][0]
            else:
                tdict[t.label()] = t[0][0]
    return tdict

if __name__ == '__main__':
    app.run()