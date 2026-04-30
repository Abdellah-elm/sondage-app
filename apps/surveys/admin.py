from django.contrib import admin
from .models import Sondage, SectionSondage, Question, Choix, LienPartage


class SectionInline(admin.TabularInline):
    model = SectionSondage
    extra = 0


class ChoixInline(admin.TabularInline):
    model = Choix
    extra = 2


@admin.register(Sondage)
class SondageAdmin(admin.ModelAdmin):
    list_display = ['titre', 'createur', 'est_actif', 'est_archive', 'cree_le', 'obtenir_nombre_reponses']
    list_filter = ['est_actif', 'est_archive', 'est_modele', 'est_anonyme']
    search_fields = ['titre', 'createur__username']
    prepopulated_fields = {'slug': ('titre',)}
    inlines = [SectionInline]
    actions = ['archiver_sondages', 'desarchiver_sondages']

    @admin.action(description='Archiver les sondages sélectionnés')
    def archiver_sondages(self, request, queryset):
        for sondage in queryset:
            sondage.archiver()

    @admin.action(description='Désarchiver les sondages sélectionnés')
    def desarchiver_sondages(self, request, queryset):
        for sondage in queryset:
            sondage.desarchiver()


@admin.register(SectionSondage)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['titre', 'sondage', 'ordre']
    list_filter = ['sondage']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['texte', 'type_question', 'est_obligatoire', 'ordre']
    list_filter = ['type_question', 'est_obligatoire']
    inlines = [ChoixInline]


@admin.register(LienPartage)
class LienPartageAdmin(admin.ModelAdmin):
    list_display = ['sondage', 'jeton', 'est_public', 'est_actif', 'cree_le']
    list_filter = ['est_public', 'est_actif']
