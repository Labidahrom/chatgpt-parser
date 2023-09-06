from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class TextsParsingSet(models.Model):
    set_name = models.CharField(max_length=500)
    total_amount = models.IntegerField()
    parsed_amount = models.IntegerField(default=0)
    is_complete = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    average_uniqueness = models.IntegerField(default=0)
    average_attempts_to_uniqueness = models.IntegerField(default=0)
    temperature = models.DecimalField(decimal_places=1, max_digits=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    failed_texts = models.TextField(default='')
    low_uniqueness_texts = models.TextField(default='')
    task_strings = models.TextField(default='')

    def __str__(self):
        return self.set_name


class Text(models.Model):
    header = models.TextField()
    text = models.TextField()
    chat_request = models.TextField()
    uniqueness = models.IntegerField()
    attempts_to_uniqueness = models.IntegerField()
    parsing_set = models.ForeignKey(TextsParsingSet, related_name="texts", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.header



