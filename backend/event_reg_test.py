import eventregistry as evr
from google.cloud import language as lang

client = lang.LanguageServiceClient()
er = evr.EventRegistry(apiKey = '3a705c62-c9ae-4c4f-9b94-a0963352b8b3')
evq = evr.QueryEventsIter(conceptUri=er.getConceptUri('donald trump'), lang=['eng'])
evq.addRequestedResult(evr.RequestEventsInfo(sortBy = 'date'))
for event in evq.execQuery(er):
    evUri = event['uri']
    print(event['location']['label']['eng'] + ',', event['location']['country']['label']['eng'])
    avgSentiment = 0
    articles = 0
    arq = evr.QueryEventArticlesIter(evUri)
    for article in arq.execQuery(er):
        document = lang.types.Document(
            content=article['body'],
            type='PLAIN_TEXT')
        try:
            sentiment = client.analyze_sentiment(document)
        except:
            break
        avgSentiment += sentiment.document_sentiment.score
        articles += 1
        if articles >= 50:
            break
    if articles == 0:
        continue
    avgSentiment = avgSentiment / articles
    print(avgSentiment)
