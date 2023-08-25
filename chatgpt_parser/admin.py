from django.contrib import admin
from chatgpt_parser.models import Text, TextsParsingSet
from django.contrib.auth.models import User


admin.site.register(Text)
admin.site.register(TextsParsingSet)
