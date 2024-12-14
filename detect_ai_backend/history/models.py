from django.db import models

from detect_ai_backend.users.models import User

# Create your models here.


class History(models.Model):
    image_url = models.TextField()
    results = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
