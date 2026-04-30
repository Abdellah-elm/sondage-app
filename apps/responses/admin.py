from django.contrib import admin
from .models import Soumission, Reponse, ReponseChoix


@admin.register(Soumission)
class SoumissionAdmin(admin.ModelAdmin):
    list_display = ['sondage', 'repondant', 'est_complete', 'commence_le', 'termine_le']
    list_filter = ['est_complete', 'sondage']
    search_fields = ['sondage__titre', 'repondant__username']
    readonly_fields = ['cle_session', 'adresse_ip', 'commence_le', 'termine_le']


@admin.register(Reponse)
class ReponseAdmin(admin.ModelAdmin):
    list_display = ['soumission', 'question', 'valeur_texte', 'valeur_echelle']
    list_filter = ['question__type_question']


@admin.register(ReponseChoix)
class ReponseChoixAdmin(admin.ModelAdmin):
    list_display = ['reponse', 'choix', 'cree_le']
