from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    path('', views.SurveyListView.as_view(), name='list'),
    path('create/', views.SurveyCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.SurveyDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.SurveyUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.SurveyDeleteView.as_view(), name='delete'),
    path('<slug:slug>/builder/', views.SurveyBuilderView.as_view(), name='builder'),
    path('<slug:slug>/duplicate/', views.SurveyDuplicateView.as_view(), name='duplicate'),
    path('<slug:slug>/archive/', views.SurveyArchiveView.as_view(), name='archive'),
    path('<slug:slug>/export/csv/', views.SurveyExportCSVView.as_view(), name='export_csv'),
    path('<slug:slug>/export/xlsx/', views.SurveyExportXLSXView.as_view(), name='export_xlsx'),
    path('<slug:slug>/share/', views.SurveyShareView.as_view(), name='share'),
    path('<slug:slug>/use-template/', views.SurveyFromTemplateView.as_view(), name='use_template'),
    path('<slug:slug>/section/add/', views.SectionCreateView.as_view(), name='section_add'),
    path('<slug:slug>/section/<int:section_id>/delete/', views.SectionDeleteView.as_view(), name='section_delete'),
    path('<slug:slug>/section/<int:section_id>/question/add/', views.QuestionCreateView.as_view(), name='question_add'),
    path('<slug:slug>/question/<int:question_id>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
]
