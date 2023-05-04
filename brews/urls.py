from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),  # welcome, login, dashboard (once logged in)
    path("unauthorized/", views.unauthorized, name="unauthorized"),
    path("feedback/", views.feedback, name="feedback"),
    path("settings/", views.feedback, name="settings"),
    path("competition/", views.competitions, name="competitions"),  # info, results (if complete), link to judge
    path("competition/<int:competition_id>/", views.competition, name="competition"),  # info, results (if complete), link to judge
    path("round/<int:round_id>/", views.round, name="round"),  # info, results (if complete), link to judge
    path("heat/<int:heat_id>/", views.heat, name="heat"),  # form to submit a judgement
    path("heat/<int:heat_id>/judgement/", views.judgement, name="judgement"),  # form to submit a judgement
    path("heat/<int:heat_id>/judgement/error/", views.judgement_error, name="judgement_error"),
    path("heat/<int:heat_id>/judgement/performance/", views.judgement_performance, name="judgement_performance"),
]