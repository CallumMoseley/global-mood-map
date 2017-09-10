import asyncio
import eventregistry as evr
import datetime
import websockets
import json
import threading
from watson_developer_cloud import ToneAnalyzerV3
from flask import Flask, request, render_template, send_from_directory
from flask_sockets import Sockets

tone_analyzer = ToneAnalyzerV3(
    username='ff55b80e-9f53-4cf3-b003-66363699e089',
    password='Mx2MnLsuWluU',
    version='2016-05-19')

er = evr.EventRegistry(apiKey = '6406cc8c-3747-4c02-b28b-f28362c25cbd')

def searchTopic(topic):
    def search(websocket):
        evq = evr.QueryEventsIter(conceptUri=er.getConceptUri(topic))
        evq.addRequestedResult(evr.RequestEventsInfo(sortBy = 'date'))
        for event in evq.execQuery(er):
            evUri = event['uri']
            if event['location'] == None:
                continue
            location = event['location']['label']['eng'] + ',', event['location']['country']['label']['eng']
            articles = 0
            arq = evr.QueryEventArticlesIter(evUri)
            avg_sentiments = {}
            for article in arq.execQuery(er):
                analysis = tone_analyzer.tone(article['body'], 'emotion')
                analysis = analysis['document_tone']['tone_categories'][0]['tones']
                if avg_sentiments == {}:
                    avg_sentiments = analysis
                else:
                    for i in range(5):
                        avg_sentiments[i]['score'] += analysis[i]['score']
                articles += 1
                if articles >= 10:
                    break
            if articles == 0:
                continue
            for i in range(5):
                avg_sentiments[i]['score'] /= articles
            response = {'location': location, 'emotions': avg_sentiments}
            print(json.dumps(response, indent=2))
            websocket.send(json.dumps(response))
    return search

app = Flask(__name__)
sockets = Sockets(app)

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def send_html(path):
    return send_from_directory('html', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)

@app.route('/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('', path)

@sockets.route('/search')
def socket(ws):
    print('receiving socket')
    search = ws.receive()
    print(search)
    searchFunc = searchTopic(search)
    searchFunc(ws)

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
server.serve_forever()
