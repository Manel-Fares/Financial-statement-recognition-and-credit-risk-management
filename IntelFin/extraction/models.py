from django.db import models

# Create your models here.

class ExtraCol(models.Model):
	
	turnover = models.CharField('turnover',max_length=100)
	market_capitalization = models.CharField('market capitalization',max_length=100)