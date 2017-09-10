import eventregistry as evr
import asyncio
import json
from watson_developer_cloud import ToneAnalyzerV3
from flask import Flask, render_template, send_from_directory
from flask_sockets import Sockets
import threading
import time

tone_analyzer = ToneAnalyzerV3(
    username='ff55b80e-9f53-4cf3-b003-66363699e089',
    password='Mx2MnLsuWluU',
    version='2016-05-19')

er = evr.EventRegistry(apiKey = '3a705c62-c9ae-4c4f-9b94-a0963352b8b3')

def searchTopic(topic):
    async def search(websocket):
        evq = evr.QueryEventsIter(conceptUri=er.getConceptUri(topic))
        evq.addRequestedResult(evr.RequestEventsInfo(sortBy = 'date'))
        for event in evq.execQuery(er):
            evUri = event['uri']
            if event['location'] == None:
                continue
            location = event['location']['label']['eng'] + ',', event['location']['country']['label']['eng']
            articles = 0
            article_content = []
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
                article_content.append({'title': article['title'], 'url': article['url']})
                if articles >= 10:
                    break
            if articles == 0:
                continue
            for i in range(5):
                avg_sentiments[i]['score'] /= articles
            response = {'location': location, 'emotions': avg_sentiments, 'articles': article_content}
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
    print('sending image from directory')
    return send_from_directory('img', path)

@app.route('/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('fonts', path)

@sockets.route('/search')
def socket(ws):
    print('receiving socket')
    search = ws.receive()
    print(search)
    searchFunc = searchTopic(search)
    time.sleep(5)
    #searchFunc(ws)
    #threading.Thread(target=searchFunc, args=(ws,))

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
server = pywsgi.WSGIServer(('', 80), app, handler_class=WebSocketHandler)
server.serve_forever()
