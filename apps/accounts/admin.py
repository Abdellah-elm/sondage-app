from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Profil


class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    verbose_name_plural = 'Profil'


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    inlines = [ProfilInline]
    list_display = ['username', 'email', 'prenom', 'nom', 'is_staff', 'date_inscription']
    list_filter = ['is_staff', 'is_superuser']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('prenom', 'nom')}),
    )


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'role', 'organisation']
    list_filter = ['role']
    search_fields = ['utilisateur__username', 'organisation']
