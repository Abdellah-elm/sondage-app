from django.urls import path
from . import views

app_name = 'responses'

urlpatterns = [
    path('<uuid:jeton>/', views.TakeSurveyView.as_view(), name='prendre'),
    path('<uuid:jeton>/merci/', views.MerciView.as_view(), name='merci'),
]
