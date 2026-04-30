from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    prenom = models.CharField(max_length=100, blank=True)
    nom = models.CharField(max_length=100, blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return self.username

    def obtenir_historique_participations(self):
        return self.soumission_set.select_related('sondage').order_by('-commence_le')

    def obtenir_sondages_crees(self):
        return self.sondage_set.order_by('-cree_le')


class Profil(models.Model):
    ROLE_VISITEUR = 'visiteur'
    ROLE_CREATEUR = 'createur'
    ROLE_ADMIN = 'admin'
    ROLES = [
        (ROLE_VISITEUR, 'Visiteur'),
        (ROLE_CREATEUR, 'Créateur'),
        (ROLE_ADMIN, 'Administrateur'),
    ]

    utilisateur = models.OneToOneField(
        Utilisateur, on_delete=models.CASCADE, related_name='profil'
    )
    role = models.CharField(max_length=50, choices=ROLES, default=ROLE_VISITEUR)
    biographie = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    organisation = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'

    def __str__(self):
        return f'Profil de {self.utilisateur.username}'

    def est_admin(self):
        return self.role == self.ROLE_ADMIN or self.utilisateur.is_superuser

    def est_createur(self):
        return self.role in (self.ROLE_CREATEUR, self.ROLE_ADMIN) or self.utilisateur.is_superuser

    def obtenir_nombre_sondages(self):
        return self.utilisateur.sondage_set.count()

    def obtenir_nombre_reponses(self):
        return self.utilisateur.soumission_set.filter(est_complete=True).count()
