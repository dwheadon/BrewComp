from django import forms
from django.forms import ModelForm
from .models import *


class CreateCompetitionForm(ModelForm):
    class Meta:
        model = Competition
        fields = ["name", "date", "criteria"]


class UpdateCompetitionForm(ModelForm):
    class Meta:
        model = Competition
        fields = ["status", "access_key"]


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


class UpdateCriterionForm(ModelForm):
    class Meta:
        model = Criterion
        fields = ['min_points', 'max_points']


class FeedbackForm(forms.Form):
    from_email = forms.EmailField(label="Email")
    subject = forms.CharField(label="Subject", max_length=100)
    message = forms.CharField(label="Message", max_length=10000, widget=forms.Textarea)
