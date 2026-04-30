from django.contrib import admin
from .models import StatistiqueSondage


@admin.register(StatistiqueSondage)
class StatistiqueSondageAdmin(admin.ModelAdmin):
    list_display = ['sondage', 'nombre_total_soumissions', 'nombre_soumissions_completes',
                    'taux_completion', 'derniere_mise_a_jour']
    readonly_fields = ['derniere_mise_a_jour']
    actions = ['actualiser_stats']

    @admin.action(description='Actualiser les statistiques')
    def actualiser_stats(self, request, queryset):
        for stat in queryset:
            stat.actualiser()
