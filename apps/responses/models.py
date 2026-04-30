from django.db import models
from django.utils import timezone


class Soumission(models.Model):
    sondage = models.ForeignKey(
        'surveys.Sondage', on_delete=models.CASCADE, related_name='soumission_set'
    )
    repondant = models.ForeignKey(
        'accounts.Utilisateur', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='soumission_set'
    )
    adresse_ip = models.GenericIPAddressField()
    cle_session = models.CharField(max_length=64)
    commence_le = models.DateTimeField(auto_now_add=True)
    termine_le = models.DateTimeField(null=True, blank=True)
    est_complete = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Soumission'
        verbose_name_plural = 'Soumissions'
        ordering = ['-commence_le']

    def __str__(self):
        return f'Soumission #{self.pk} — {self.sondage.titre}'

    def obtenir_anonyme(self):
        return self.sondage.est_anonyme or self.repondant is None

    def temps_expire(self):
        if not self.sondage.a_minuteur():
            return False
        duree_max = self.sondage.duree_limite_minutes * 60
        elapsed = (timezone.now() - self.commence_le).total_seconds()
        return elapsed > duree_max

    def obtenir_taux_completion_global(self):
        total = self.sondage.sections.aggregate(
            total=models.Count('questions')
        )['total'] or 0
        if total == 0:
            return 100.0
        repondues = self.reponses.count()
        return round(repondues / total * 100, 1)

    def obtenir_duree(self):
        if self.termine_le:
            return self.termine_le - self.commence_le
        return timezone.now() - self.commence_le

    def obtenir_temps_restant(self):
        if not self.sondage.a_minuteur():
            return None
        duree_max = self.sondage.duree_limite_minutes * 60
        elapsed = (timezone.now() - self.commence_le).total_seconds()
        return max(0, int(duree_max - elapsed))

    def marquer_complete(self):
        self.est_complete = True
        self.termine_le = timezone.now()
        self.save()
        from apps.analytics.models import StatistiqueSondage
        stat, _ = StatistiqueSondage.objects.get_or_create(sondage=self.sondage)
        stat.actualiser()


class Reponse(models.Model):
    soumission = models.ForeignKey(
        Soumission, on_delete=models.CASCADE, related_name='reponses'
    )
    question = models.ForeignKey(
        'surveys.Question', on_delete=models.CASCADE, related_name='reponses'
    )
    valeur_texte = models.TextField(blank=True)
    valeur_echelle = models.IntegerField(null=True, blank=True)
    choix_selectionnes = models.ManyToManyField(
        'surveys.Choix', blank=True, through='ReponseChoix', related_name='reponses'
    )

    class Meta:
        verbose_name = 'Réponse'
        verbose_name_plural = 'Réponses'

    def __str__(self):
        return f'Réponse à "{self.question.texte[:40]}"'

    def obtenir_valeur_affichage(self):
        from apps.surveys.models import Question
        if self.question.type_question == Question.TYPE_TEXTE:
            return self.valeur_texte
        if self.question.type_question == Question.TYPE_ECHELLE:
            return str(self.valeur_echelle) if self.valeur_echelle is not None else ''
        choix = self.choix_selectionnes.all()
        return ', '.join(c.texte for c in choix)

class ReponseChoix(models.Model):
    reponse = models.ForeignKey(Reponse, on_delete=models.CASCADE, related_name='reponse_choix')
    choix = models.ForeignKey('surveys.Choix', on_delete=models.CASCADE, related_name='reponse_choix')
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Réponse — Choix'
        verbose_name_plural = 'Réponses — Choix'
        unique_together = [('reponse', 'choix')]
