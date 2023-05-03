from django.contrib import admin

from .models import *

admin.site.register(Entry)
#admin.site.register(Criterion)
admin.site.register(Rank)
admin.site.register(Ranking)
admin.site.register(Competition)
admin.site.register(Round)
admin.site.register(Heat)
admin.site.register(Judgement)


@admin.display(description="Criterion with connnections")
def criterion_with_connections(self):
    if self.competition_set.count() != 0:
        connection = self.competition_set.all().first()
    elif self.heat_set.count() != 0:
        connection = self.heat_set.all().first()
    else:
        connection = None
    return self.name + ": " + str(self.min_points) + "-" + str(self.max_points) + " points for " + str(connection)

@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    list_display = [criterion_with_connections]
