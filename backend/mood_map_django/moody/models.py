from django.db import models

class Event(models.Model):
    common_date = models.DateTimeField('date published')
    sentiment_score = models.FloatField()
    sentiment_mag = models.FloatField()

