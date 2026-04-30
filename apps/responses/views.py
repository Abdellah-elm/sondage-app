import hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from apps.surveys.models import LienPartage, Question, Choix
from apps.analytics.models import StatistiqueSondage
from apps.dashboard.models import Notification
from .models import Soumission, Reponse, ReponseChoix
from .forms import DynamicResponseForm, PasswordSondageForm

THEMES_CSS = {
    'defaut':       {'header': 'linear-gradient(135deg,#3b82f6,#1d4ed8)', 'border': '#3b82f6'},
    'moderne':      {'header': 'linear-gradient(135deg,#7c3aed,#4f46e5)', 'border': '#7c3aed'},
    'professionnel':{'header': 'linear-gradient(135deg,#059669,#047857)', 'border': '#059669'},
    'chaleureux':   {'header': 'linear-gradient(135deg,#f97316,#dc2626)', 'border': '#f97316'},
}


def _cle_session(request, sondage_id):
    if not request.session.session_key:
        request.session.create()
    base = f"{request.session.session_key}_{sondage_id}"
    return hashlib.sha256(base.encode()).hexdigest()[:64]


def _get_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '127.0.0.1')


class TakeSurveyView(View):
    template_name = 'responses/take.html'
    password_template = 'responses/password_required.html'

    def _get_lien(self, jeton):
        return get_object_or_404(LienPartage, jeton=jeton, est_actif=True)

    def _get_theme(self, sondage):
        return THEMES_CSS.get(sondage.theme, THEMES_CSS['defaut'])

    def get(self, request, jeton):
        lien = self._get_lien(jeton)
        sondage = lien.sondage

        if not sondage.est_actif or sondage.est_archive:
            return render(request, 'responses/ferme.html', {'sondage': sondage})

        if sondage.est_expire():
            return render(request, 'responses/expire.html', {'sondage': sondage})

        if sondage.max_reponses:
            nb_complete = sondage.soumission_set.filter(est_complete=True).count()
            if nb_complete >= sondage.max_reponses:
                return render(request, 'responses/limite_reponses.html', {'sondage': sondage})

        session_key_mdp = f'mdp_ok_{sondage.pk}'
        if sondage.est_protege_par_mdp() and not request.session.get(session_key_mdp):
            return render(request, self.password_template, {
                'sondage': sondage, 'form': PasswordSondageForm(), 'jeton': jeton,
                'theme': self._get_theme(sondage),
            })

        if request.session.get(f'soumis_{sondage.pk}'):
            return redirect('responses:merci', jeton=jeton)

        cle = _cle_session(request, sondage.pk)
        soumission, _ = Soumission.objects.get_or_create(
            sondage=sondage,
            cle_session=cle,
            est_complete=False,
            defaults={
                'repondant': request.user if request.user.is_authenticated else None,
                'adresse_ip': _get_ip(request),
            }
        )

        questions = Question.objects.filter(
            section__sondage=sondage
        ).select_related('section', 'condition_choix').prefetch_related('choix').order_by('section__ordre', 'ordre')

        form = DynamicResponseForm(questions)
        questions_and_fields = [(q, form[f'q_{q.pk}']) for q in questions]

        return render(request, self.template_name, {
            'sondage': sondage,
            'lien': lien,
            'form': form,
            'questions': questions,
            'questions_and_fields': questions_and_fields,
            'soumission': soumission,
            'temps_restant': soumission.obtenir_temps_restant(),
            'theme': self._get_theme(sondage),
        })

    def post(self, request, jeton):
        lien = self._get_lien(jeton)
        sondage = lien.sondage

        if not sondage.est_actif or sondage.est_archive:
            return render(request, 'responses/ferme.html', {'sondage': sondage})

        if sondage.est_expire():
            return render(request, 'responses/expire.html', {'sondage': sondage})

        if sondage.max_reponses:
            nb_complete = sondage.soumission_set.filter(est_complete=True).count()
            if nb_complete >= sondage.max_reponses:
                return render(request, 'responses/limite_reponses.html', {'sondage': sondage})

        session_key_mdp = f'mdp_ok_{sondage.pk}'
        if sondage.est_protege_par_mdp() and not request.session.get(session_key_mdp):
            form_mdp = PasswordSondageForm(request.POST)
            if form_mdp.is_valid():
                if sondage.verifier_mot_de_passe(form_mdp.cleaned_data['mot_de_passe']):
                    request.session[session_key_mdp] = True
                    return redirect('responses:prendre', jeton=jeton)
            return render(request, self.password_template, {
                'sondage': sondage, 'form': form_mdp, 'jeton': jeton, 'erreur': True,
                'theme': self._get_theme(sondage),
            })

        cle = _cle_session(request, sondage.pk)
        soumission = get_object_or_404(Soumission, sondage=sondage, cle_session=cle, est_complete=False)

        if soumission.temps_expire():
            soumission.delete()
            return render(request, 'responses/expire.html', {'sondage': sondage})

        questions = Question.objects.filter(
            section__sondage=sondage
        ).select_related('section', 'condition_choix').prefetch_related('choix').order_by('section__ordre', 'ordre')

        form = DynamicResponseForm(questions, request.POST)
        if form.is_valid():
            for question in questions:
                field_name = f'q_{question.pk}'
                valeur = form.cleaned_data.get(field_name)

                reponse, _ = Reponse.objects.get_or_create(soumission=soumission, question=question)
                reponse.valeur_texte = ''
                reponse.valeur_echelle = None

                if question.type_question == Question.TYPE_TEXTE:
                    reponse.valeur_texte = valeur or ''
                    reponse.save()
                elif question.type_question == Question.TYPE_ECHELLE:
                    reponse.valeur_echelle = valeur
                    reponse.save()
                elif question.type_question == Question.TYPE_CHOIX_UNIQUE:
                    reponse.save()
                    ReponseChoix.objects.filter(reponse=reponse).delete()
                    if valeur:
                        ReponseChoix.objects.create(reponse=reponse, choix=valeur)
                elif question.type_question == Question.TYPE_CHOIX_MULTIPLE:
                    reponse.save()
                    ReponseChoix.objects.filter(reponse=reponse).delete()
                    for choix in (valeur or []):
                        ReponseChoix.objects.create(reponse=reponse, choix=choix)

            soumission.marquer_complete()

            Notification.objects.create(
                utilisateur=sondage.createur,
                sondage=sondage,
                message=f'Nouvelle réponse reçue pour « {sondage.titre} ».',
                type_notification=Notification.TYPE_NOUVELLE_REPONSE,
            )

            request.session[f'soumis_{sondage.pk}'] = True
            return redirect('responses:merci', jeton=jeton)

        questions_and_fields = [(q, form[f'q_{q.pk}']) for q in questions]
        return render(request, self.template_name, {
            'sondage': sondage,
            'lien': lien,
            'form': form,
            'questions': questions,
            'questions_and_fields': questions_and_fields,
            'soumission': soumission,
            'temps_restant': soumission.obtenir_temps_restant(),
            'theme': self._get_theme(sondage),
        })


class MerciView(View):
    def get(self, request, jeton):
        lien = get_object_or_404(LienPartage, jeton=jeton)
        return render(request, 'responses/merci.html', {'sondage': lien.sondage})
