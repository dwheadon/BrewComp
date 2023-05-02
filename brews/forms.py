from django.forms import ModelForm
from .models import *


class CreateCompetitionForm(ModelForm):
    class Meta:
        model = Competition
        fields = ["name", "date", "criteria"]


class UpdateCompetitionForm(ModelForm):
    class Meta:
        model = Competition
        fields = ["status"]


class EntryForm(ModelForm):
    class Meta:
        model = Entry
        fields = ['name']


class RoundForm(ModelForm):
    class Meta:
        model = Round
        fields = []


class UpdateRoundForm(ModelForm):
    class Meta:
        model = Round
        fields = ['status']


class CreateHeatForm(ModelForm):
    class Meta:
        model = Heat
        fields = []


class UpdateHeatForm(ModelForm):
    class Meta:
        model = Heat
        fields = ['status', 'entries', 'winners']


