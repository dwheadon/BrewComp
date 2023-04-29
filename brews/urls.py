from django.urls import path

from . import views

urlpatterns = [
    path("", views.competitions, name="home"),  # welcome, login, dashboard (once logged in)
    path("feedback/", views.feedback, name="feedback"),
    path("competition/<int:competition_id>/", views.competition, name="competition"),  # info, results (if complete), link to judge
    path("competition/<int:competition_id>/judgement/", views.judgement, name="judgement"),  # form to submit a judgement
    path("competition/<int:competition_id>/judgement/error/", views.judgement_error, name="judgement_error")
]