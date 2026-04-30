from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'type_notification', 'est_lu', 'cree_le']
    list_filter = ['type_notification', 'est_lu']
    search_fields = ['utilisateur__username', 'message']
    actions = ['marquer_lu']

    @admin.action(description='Marquer comme lues')
    def marquer_lu(self, request, queryset):
        queryset.update(est_lu=True)
