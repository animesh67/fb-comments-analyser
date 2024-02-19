from django.db import models

# Create your models here.
class User(models.Model):
	username = models.TextField()
	password = models.TextField()


class Source_detail(models.Model):
	source=models.TextField()
	source_url=models.TextField()
	severe_toxic=models.FloatField()
	toxic=models.FloatField()
	identity_hate=models.FloatField()
	insult=models.FloatField()
	threat=models.FloatField()
	obscene=models.FloatField()
	non_toxic=models.FloatField()