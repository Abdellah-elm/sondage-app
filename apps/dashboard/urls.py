from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.SmartDashboardView.as_view(), name='smart'),

    path('createur/', views.DashboardView.as_view(), name='index'),

    path('participant/', views.ParticipantDashboardView.as_view(), name='participant'),
    path('disponibles/', views.SondagesDisponiblesView.as_view(), name='sondages_disponibles'),
    path('historique/', views.MonHistoriqueView.as_view(), name='mon_historique'),

    path('notifications/', views.NotificationsView.as_view(), name='notifications'),
    path('notifications/<int:pk>/lu/', views.NotificationMarkReadView.as_view(), name='notif_read'),

    path('admin/', views.AdminDashboardView.as_view(), name='admin'),
    path('admin/utilisateurs/', views.AdminUsersView.as_view(), name='admin_users'),
    path('admin/utilisateurs/<int:pk>/role/', views.AdminChangeRoleView.as_view(), name='admin_change_role'),
    path('admin/sondages/', views.AdminSurveysView.as_view(), name='admin_surveys'),
]
