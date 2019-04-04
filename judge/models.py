from django.db import models

# Create your models here.
class Problem(models.Model):
    statement = models.CharField(max_length=5000)