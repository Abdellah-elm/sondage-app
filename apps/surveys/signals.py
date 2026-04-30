from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sondage, LienPartage


@receiver(post_save, sender=Sondage)
def creer_objets_lies(sender, instance, created, **kwargs):
    if created:
        # Créer un lien de partage par défaut
        LienPartage.objects.get_or_create(sondage=instance)
        # Créer les statistiques
        from apps.analytics.models import StatistiqueSondage
        StatistiqueSondage.objects.get_or_create(sondage=instance)
