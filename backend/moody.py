import asyncio
import eventregistry as evr
import datetime
import websockets
import json
from watson_developer_cloud import ToneAnalyzerV3

tone_analyzer = ToneAnalyzerV3(
    username='ff55b80e-9f53-4cf3-b003-66363699e089',
    password='Mx2MnLsuWluU',
    version='2016-05-19')

er = evr.EventRegistry(apiKey = '6406cc8c-3747-4c02-b28b-f28362c25cbd')

def searchTopic(topic):
    def search(websocket, path):
        evq = evr.QueryEventsIter(conceptUri=er.getConceptUri(topic))
        evq.addRequestedResult(evr.RequestEventsInfo(sortBy = 'date'))
        for event in evq.execQuery(er):
            evUri = event['uri']
            if event['location'] == None:
                continue
            location = event['location']['label']['eng'] + ',', event['location']['country']['label']['eng']
            avgSentiment = 0
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
    return search


