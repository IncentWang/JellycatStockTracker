from django.db import models

# Create your models here.
class Toy(models.Model):
    url = models.CharField(max_length=200)
    sku = models.CharField(max_length=50)
    name = models.CharField(max_length=200)

class User(models.Model):
    email = models.CharField(max_length=200)

class Watching(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watched_toy = models.ForeignKey(Toy, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    get_result = models.BooleanField()
