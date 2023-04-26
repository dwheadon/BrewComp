from django.contrib import admin

from .models import *

admin.site.register(Entry)
admin.site.register(Criterion)
admin.site.register(Rank)
admin.site.register(Ranking)
admin.site.register(Competition)
admin.site.register(Judgement)
