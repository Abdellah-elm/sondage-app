import json
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.views import View
from apps.accounts.mixins import RequireCreateurMixin
from apps.surveys.models import Sondage, Question
from apps.responses.models import Reponse, Soumission
from .models import StatistiqueSondage


class SurveyResultsView(RequireCreateurMixin, View):
    template_name = 'analytics/results.html'

    def get(self, request, slug):
        sondage = get_object_or_404(Sondage, slug=slug)
        profil = request.user.profil
        if sondage.createur != request.user and not profil.est_admin():
            raise PermissionDenied

        stat, _ = StatistiqueSondage.objects.get_or_create(sondage=sondage)
        stat.actualiser()

        date_debut = request.GET.get('date_debut', '')
        date_fin = request.GET.get('date_fin', '')
        criteres = {}
        if date_debut:
            try:
                criteres['date_debut'] = date.fromisoformat(date_debut)
            except ValueError:
                pass
        if date_fin:
            try:
                criteres['date_fin'] = date.fromisoformat(date_fin)
            except ValueError:
                pass

        questions = Question.objects.filter(
            section__sondage=sondage
        ).prefetch_related('choix').order_by('section__ordre', 'ordre')

        questions_data = []
        for q in questions:
            reponses_qs = Reponse.objects.filter(question=q, soumission__est_complete=True)
            if criteres.get('date_debut'):
                reponses_qs = reponses_qs.filter(soumission__termine_le__date__gte=criteres['date_debut'])
            if criteres.get('date_fin'):
                reponses_qs = reponses_qs.filter(soumission__termine_le__date__lte=criteres['date_fin'])

            nb_reponses = reponses_qs.count()
            total = sondage.soumission_set.filter(est_complete=True).count()
            taux = round(nb_reponses / total * 100, 1) if total else 0.0

            qdata = {
                'question': q,
                'nb_reponses': nb_reponses,
                'taux_reponses': taux,
                'chart_data': None,
                'moyenne': None,
                'textes_libres': [],
            }

            if q.est_type_choix():
                dist = {}
                for choix in q.obtenir_choix():
                    from apps.responses.models import ReponseChoix
                    nb = ReponseChoix.objects.filter(
                        choix=choix, reponse__soumission__est_complete=True,
                        **({'reponse__soumission__termine_le__date__gte': criteres['date_debut']} if criteres.get('date_debut') else {}),
                        **({'reponse__soumission__termine_le__date__lte': criteres['date_fin']} if criteres.get('date_fin') else {}),
                    ).count()
                    dist[choix.texte] = nb
                qdata['chart_data'] = json.dumps({'labels': list(dist.keys()), 'data': list(dist.values())})

            elif q.est_type_echelle():
                valeurs = list(reponses_qs.filter(valeur_echelle__isnull=False).values_list('valeur_echelle', flat=True))
                if valeurs:
                    qdata['moyenne'] = round(sum(valeurs) / len(valeurs), 2)
                    distribution = {str(v): valeurs.count(v) for v in range(q.echelle_min, q.echelle_max + 1)}
                    qdata['chart_data'] = json.dumps({'labels': list(distribution.keys()), 'data': list(distribution.values())})

            elif q.est_type_texte():
                qdata['textes_libres'] = list(
                    reponses_qs.exclude(valeur_texte='').values_list('valeur_texte', flat=True)[:20]
                )

            questions_data.append(qdata)

        soumissions_par_jour = stat.obtenir_soumissions_par_jour()
        chart_soumissions = json.dumps({
            'labels': list(soumissions_par_jour.keys()),
            'data': list(soumissions_par_jour.values()),
        })

        return render(request, self.template_name, {
            'sondage': sondage,
            'stat': stat,
            'resume': stat.obtenir_resume(),
            'questions_data': questions_data,
            'chart_soumissions': chart_soumissions,
            'date_debut': date_debut,
            'date_fin': date_fin,
        })
