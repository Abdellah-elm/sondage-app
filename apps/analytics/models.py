from django.db import models


class StatistiqueSondage(models.Model):
    sondage = models.OneToOneField(
        'surveys.Sondage', on_delete=models.CASCADE, related_name='statistiquesondage'
    )
    nombre_total_soumissions = models.IntegerField(default=0)
    nombre_soumissions_completes = models.IntegerField(default=0)
    taux_completion = models.FloatField(default=0.0)
    duree_moyenne_reponse = models.DurationField(null=True, blank=True)
    derniere_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Statistique sondage'
        verbose_name_plural = 'Statistiques sondages'

    def __str__(self):
        return f'Stats — {self.sondage.titre}'

    def calculer_taux_completion(self):
        total = self.nombre_total_soumissions
        if total == 0:
            return 0.0
        return round(self.nombre_soumissions_completes / total * 100, 1)

    def calculer_duree_moyenne(self):
        from apps.responses.models import Soumission
        from django.db.models import Avg, F, ExpressionWrapper, DurationField
        result = Soumission.objects.filter(
            sondage=self.sondage,
            est_complete=True,
            termine_le__isnull=False,
        ).aggregate(
            duree_moy=Avg(
                ExpressionWrapper(
                    F('termine_le') - F('commence_le'),
                    output_field=DurationField()
                )
            )
        )
        return result['duree_moy']

    def obtenir_soumissions_par_jour(self):
        from apps.responses.models import Soumission
        from django.db.models.functions import TruncDate
        from django.db.models import Count
        qs = (
            Soumission.objects.filter(sondage=self.sondage, est_complete=True)
            .annotate(jour=TruncDate('termine_le'))
            .values('jour')
            .annotate(nb=Count('id'))
            .order_by('jour')
        )
        return {str(item['jour']): item['nb'] for item in qs}

    def obtenir_resume(self):
        return {
            'total_soumissions': self.nombre_total_soumissions,
            'completes': self.nombre_soumissions_completes,
            'taux_completion': self.taux_completion,
            'duree_moyenne': str(self.duree_moyenne_reponse) if self.duree_moyenne_reponse else None,
        }

    def filtrer_reponses(self, criteres):
        from apps.responses.models import Reponse
        qs = Reponse.objects.filter(soumission__sondage=self.sondage)
        if criteres.get('date_debut'):
            qs = qs.filter(soumission__termine_le__date__gte=criteres['date_debut'])
        if criteres.get('date_fin'):
            qs = qs.filter(soumission__termine_le__date__lte=criteres['date_fin'])
        return qs

    def actualiser(self):
        from apps.responses.models import Soumission
        soumissions = Soumission.objects.filter(sondage=self.sondage)
        self.nombre_total_soumissions = soumissions.count()
        self.nombre_soumissions_completes = soumissions.filter(est_complete=True).count()
        self.taux_completion = self.calculer_taux_completion()
        self.duree_moyenne_reponse = self.calculer_duree_moyenne()
        self.save()
