import eventregistry as evr
import json
from watson_developer_cloud import ToneAnalyzerV3

tone_analyzer = ToneAnalyzerV3(
    username='ff55b80e-9f53-4cf3-b003-66363699e089',
    password='Mx2MnLsuWluU',
    version='2016-05-19')

er = evr.EventRegistry(apiKey = '6406cc8c-3747-4c02-b28b-f28362c25cbd')
evq = evr.QueryEventsIter(conceptUri=er.getConceptUri('hurricane'))
evq.addRequestedResult(evr.RequestEventsInfo(sortBy = 'date'))
for event in evq.execQuery(er):
    evUri = event['uri']
    if event['location'] == None:
        continue
    print(event['location']['label']['eng'] + ',', event['location']['country']['label']['eng'])
    avgSentiment = 0
    articles = 0
    arq = evr.QueryEventArticlesIter(evUri)
    for article in arq.execQuery(er):
        analysis = tone_analyzer.tone(article['body'], 'emotion')
        print(json.dumps(analysis, indent=2))
        articles += 1
        if articles >= 5:
            break
    if articles == 0:
        continue
    avgSentiment = avgSentiment / articles
    print(avgSentiment)
