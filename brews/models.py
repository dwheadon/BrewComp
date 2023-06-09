from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
import random
import string
from django.contrib import admin

# class Brewer(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)


# class StyleCategory(models.Model):
#     number = models.IntegerField()
#     name = models.CharField(max_length=255)
#     description = models.TimeField()


# class StyleSubCategory(StyleCategory):
#     letter = models.CharField(max_length=255)
#     name = models.CharField(max_length=255)


# class Style(models.Model):
#     category = models.ForeignKey(StyleCategory)
#     name = models.CharField(max_length=255)
#     ibu_min = models.PositiveIntegerField()
#     ibu_max = models.PositiveIntegerField()
#     srm_min = models.PositiveIntegerField()
#     srm_max = models.PositiveIntegerField()
#     og_min = models.FloatField()
#     og_max = models.FloatField()
#     fg_min = models.FloatField()
#     fg_max = models.FloatField()
#     abv_min = models.FloatField()
#     abv_max = models.FloatField()
#     overall_impression = models.TextField()
#     appearance = models.TextField()
#     aroma = models.TextField()
#     flavor = models.TextField()
#     mouthfeel = models.TextField()
#     comments = models.TextField()
#     history = models.TextField()
#     characteristic_ingredients = models.TextField()
#     style_comparison = models.TextField()


# class Brew(models.Model):
#     brewer = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     # style = models.ForeignKey(Style, on_delete=models.SET_NULL)

#     def __str__(self) -> str:
#         return str(self.brewer) + ": " + self.name
    
#     class Meta:
#         ordering = ['brewer', 'name']


# class Judge(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     brewer = models.ForeignKey(Brewer, on_delete=models.CASCADE)


# ??? Should we separate the criteria from the max_points?
class Criterion(models.Model):
    name = models.CharField(max_length=255)  # flavor, aroma, overall, mouthfeel, appearance
    min_points = models.PositiveSmallIntegerField()
    max_points = models.PositiveSmallIntegerField()  # 20, 12, 10, 5, 3 respectively

    def __str__(self) -> str:
        return self.name + ": " + str(self.min_points) + "-" + str(self.max_points) + " points"
        
    class Meta:
        ordering = ['-max_points', 'name']
        verbose_name_plural = "criteria"


# Final results that are accumulated / calculated for a brew
# class Score(models.Model):
#     judge = models.ForeignKey(User, on_delete=models.CASCADE)
#     entry = models.ForeignKey(Entry, on_delte=models.CASCADE)
#     flavor = models.PositiveSmallIntegerField(max=20)
#     aroma = models.PositiveSmallIntegerField(max=12)
#     overall = models.PositiveSmallIntegerField(max=10)
#     mouthfeel = models.PositiveSmallIntegerField(max=5)
#     appearance = models.PositiveSmallIntegerField(max=3)


def get_random_labels():
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    random.shuffle(labels)
    return "".join(labels)


def get_random_access_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class Competition(models.Model):
    class Status(models.TextChoices):
        REGISTRATION = "REGR", _("Setup")  # for entries
        OPEN = "OPEN", _("Open")  # for judging
        CLOSED = "CLSD", _("Closed")  # for judging
        COMPLETE = "COMP", _("Complete")  # ready to show results

    date = models.DateField()
    name = models.CharField(max_length=255, blank=True)
    labels = models.CharField(max_length=26, default=get_random_labels)
    # location = models.CharField(max_length=255)
    # judges = models.ManyToManyField(User, blank=True)  # registered: need to know if everyone registered has submitted or if still waiting on someone
    # entries = models.ManyToManyField(Entry, blank=True)  # must be finalized before any scoresheets are submitted
    criteria = models.ManyToManyField(Criterion)  # the general range for a particular competition
    # judgments = models.ManyToManyField(Judgement)  # must contain one per registered judge before you tabulate the results
    status = models.CharField(max_length=4, choices=Status.choices, default=Status.REGISTRATION)
    access_key = models.CharField(max_length=10, default=get_random_access_key, blank=True, null=True)

    def get_next_label(self):
        label = self.labels[0]
        self.labels = self.labels[1:]
        self.save()
        return label
    
    def get_next_round(self):
        rounds = Round.objects.filter(competition=self)
        if rounds.count() == 0:
            return 1
        return rounds.last().number + 1

    def __str__(self) -> str:
        return str(self.date) + " " + self.name
    
    class Meta:
        ordering = ['-date', 'name']


class Entry(models.Model):
    competition = models.ForeignKey(Competition, models.CASCADE)
    label = models.CharField(max_length=1)  # Anonymous label like: A, B, C, D...
    # brew = models.ForeignKey(Brew, on_delete=models.CASCADE)
    brewer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # of the brew

    def __str__(self) -> str:
        return str(self.competition) + ": [" + self.label + "] " + str(self.brewer) + "'s " + str(self.name)
    
    class Meta:
        ordering = ['competition', 'label']
        verbose_name_plural = "entries"
        unique_together = ['competition', 'label']


class Round(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=4, choices=Competition.Status.choices, default=Competition.Status.REGISTRATION)
    entries = models.ManyToManyField(Entry)

    def get_next_heat(self):
        heats = Heat.objects.filter(round=self)
        if heats.count() == 0:
            return 1
        return heats.last().number + 1

    def __str__(self) -> str:
        return "Round " + str(self.number) + " for " + str(self.competition)
    
    class Meta:
        ordering = ['competition', 'number']


class Heat(models.Model):  # A sub-competition
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField()
    criteria = models.ManyToManyField(Criterion, blank=True)  # The specific range for entries in this heat
    status = models.CharField(max_length=4, choices=Competition.Status.choices, default=Competition.Status.REGISTRATION)
    entries = models.ManyToManyField(Entry, blank=True, related_name="heats_entered")
    winners = models.ManyToManyField(Entry, blank=True, related_name="heats_won")

    def __str__(self) -> str:
        return "Heat " + str(self.round.number) + "-" + str(self.number) + " for " + str(self.round.competition)
    
    class Meta:
        ordering = ['round', 'number']


class Judgement(models.Model):
    heat = models.ForeignKey(Heat, on_delete=models.CASCADE)
    judge = models.ForeignKey(User, on_delete=models.CASCADE)  # needs to be registered for this competition
    # rankings = models.ManyToManyField(Ranking)  # must be one per criteria for this competition

    def __str__(self) -> str:
        return str(self.heat) + ": " + str(self.judge)
    
    class Meta:
        ordering = ['heat', 'judge']  # !!! add a time field and order by time rather than judge
        unique_together = ['heat', 'judge']


class Ranking(models.Model):
    judgement = models.ForeignKey(Judgement, on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)  # needs to be one of the criteria that's being used for this competition
    # ranks = models.ManyToManyField(Rank)  # must be one for each of the entries in this competition and all must have a different rank

    def __str__(self) -> str:
        return str(self.judgement) + ": " + str(self.criterion)
    
    class Meta:
        ordering = ['judgement', 'criterion']


class Rank(models.Model):
    # judgement = models.ForeignKey(Judgement, on_delete=models.CASCADE)
    ranking = models.ForeignKey(Ranking, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    ordinal = models.PositiveSmallIntegerField()  # 1=best, competition.entries.count()=worst

    def __str__(self) -> str:
        return str(self.entry) + ": " + str(self.ranking.criterion) + " " + str(self.ordinal)
    
    class Meta:
        ordering = ['ranking', 'ordinal', 'entry']
        unique_together = ['ranking', 'ordinal']


