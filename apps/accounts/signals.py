from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Utilisateur, Profil


@receiver(post_save, sender=Utilisateur)
def creer_ou_sync_profil(sender, instance, created, **kwargs):
    if created:
        role = Profil.ROLE_ADMIN if instance.is_superuser else Profil.ROLE_VISITEUR
        Profil.objects.create(utilisateur=instance, role=role)
    else:
        profil, _ = Profil.objects.get_or_create(utilisateur=instance)
        if instance.is_superuser and profil.role != Profil.ROLE_ADMIN:
            profil.role = Profil.ROLE_ADMIN
            profil.save()
        elif not instance.is_superuser and profil.role == Profil.ROLE_ADMIN:
            profil.role = Profil.ROLE_VISITEUR
            profil.save()
