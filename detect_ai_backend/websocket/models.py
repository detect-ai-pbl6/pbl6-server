from django.db import models

from detect_ai_backend.users.models import User

# Create your models here.


class Websocket(models.Model):
    connection_id = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
