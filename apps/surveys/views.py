import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden
from apps.accounts.mixins import RequireCreateurMixin
from apps.accounts.models import Profil
from .models import Sondage, SectionSondage, Question, Choix, LienPartage
from .forms import SondageForm, SectionForm, QuestionForm


def _verifier_acces_sondage(sondage, user):
    """Lève PermissionDenied si l'utilisateur n'est ni le créateur ni un admin."""
    profil = getattr(user, 'profil', None)
    if sondage.createur != user and not (profil and profil.est_admin()):
        raise PermissionDenied


class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return redirect('accounts:connexion')


class SurveyListView(RequireCreateurMixin, ListView):
    template_name = 'surveys/list.html'
    context_object_name = 'sondages'
    paginate_by = 12

    def get_queryset(self):
        qs = Sondage.objects.filter(createur=self.request.user)
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(titre__icontains=q)
        filtre = self.request.GET.get('filtre', 'tous')
        if filtre == 'actif':
            qs = qs.filter(est_actif=True, est_archive=False)
        elif filtre == 'archive':
            qs = qs.filter(est_archive=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['filtre'] = self.request.GET.get('filtre', 'tous')
        context['total'] = Sondage.objects.filter(createur=self.request.user).count()
        context['modeles'] = Sondage.objects.filter(est_modele=True).order_by('-cree_le')[:6]
        return context


class SurveyFromTemplateView(RequireCreateurMixin, View):
    def post(self, request, slug):
        modele = get_object_or_404(Sondage, slug=slug, est_modele=True)
        nouveau = modele.dupliquer()
        nouveau.createur = request.user
        nouveau.est_modele = False
        nouveau.save()
        messages.success(request, f'Sondage créé depuis le modèle « {modele.titre} ».')
        return redirect('surveys:builder', slug=nouveau.slug)


class SurveyCreateView(RequireCreateurMixin, CreateView):
    model = Sondage
    form_class = SondageForm
    template_name = 'surveys/create.html'

    def form_valid(self, form):
        sondage = form.save(commit=False)
        sondage.createur = self.request.user
        sondage.save()
        SectionSondage.objects.create(sondage=sondage, titre='Section 1', ordre=0)
        messages.success(self.request, f'Sondage « {sondage.titre} » créé. Ajoutez vos questions.')
        return redirect('surveys:builder', slug=sondage.slug)


class SurveyDetailView(RequireCreateurMixin, DetailView):
    model = Sondage
    template_name = 'surveys/detail.html'
    context_object_name = 'sondage'

    def get_object(self):
        sondage = get_object_or_404(Sondage, slug=self.kwargs['slug'])
        if sondage.createur != self.request.user and not getattr(getattr(self.request.user, 'profil', None), 'est_admin', lambda: False)():
            raise PermissionDenied
        return sondage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sondage = self.object
        from apps.analytics.models import StatistiqueSondage
        stat, _ = StatistiqueSondage.objects.get_or_create(sondage=sondage)
        context['stats'] = stat.obtenir_resume()
        context['lien_principal'] = sondage.liens.filter(est_actif=True).first()
        context['sections'] = sondage.sections.prefetch_related('questions').order_by('ordre')
        return context


class SurveyUpdateView(RequireCreateurMixin, UpdateView):
    model = Sondage
    form_class = SondageForm
    template_name = 'surveys/edit.html'
    context_object_name = 'sondage'

    def get_object(self):
        sondage = get_object_or_404(Sondage, slug=self.kwargs['slug'])
        if sondage.createur != self.request.user and not getattr(getattr(self.request.user, 'profil', None), 'est_admin', lambda: False)():
            raise PermissionDenied
        return sondage

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Sondage mis à jour avec succès.')
        return response

    def get_success_url(self):
        return reverse('surveys:detail', kwargs={'slug': self.object.slug})


class SurveyDeleteView(RequireCreateurMixin, DeleteView):
    model = Sondage
    template_name = 'surveys/delete_confirm.html'
    success_url = reverse_lazy('surveys:list')
    context_object_name = 'sondage'

    def get_object(self):
        sondage = get_object_or_404(Sondage, slug=self.kwargs['slug'])
        if sondage.createur != self.request.user and not getattr(getattr(self.request.user, 'profil', None), 'est_admin', lambda: False)():
            raise PermissionDenied
        return sondage

    def form_valid(self, form):
        titre = self.object.titre
        response = super().form_valid(form)
        messages.success(self.request, f'Sondage « {titre} » supprimé définitivement.')
        return response


class SurveyBuilderView(RequireCreateurMixin, DetailView):
    model = Sondage
    template_name = 'surveys/builder.html'
    context_object_name = 'sondage'

    def get_object(self):
        sondage = get_object_or_404(Sondage, slug=self.kwargs['slug'])
        if sondage.createur != self.request.user and not getattr(getattr(self.request.user, 'profil', None), 'est_admin', lambda: False)():
            raise PermissionDenied
        return sondage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sondage = self.object
        sections = list(sondage.sections.prefetch_related('questions__choix').order_by('ordre'))
        context['sections'] = sections
        context['total_questions'] = sum(s.questions.count() for s in sections)
        context['section_form'] = SectionForm()
        context['question_form'] = QuestionForm()
        context['question_types'] = Question.TYPES
        return context


class SurveyDuplicateView(RequireCreateurMixin, View):
    def post(self, request, slug):
        sondage = get_object_or_404(Sondage, slug=slug)
        if sondage.createur != request.user and not getattr(getattr(request.user, 'profil', None), 'est_admin', lambda: False)():
            return HttpResponseForbidden()
        nouveau = sondage.dupliquer()
        messages.success(request, f'Sondage dupliqué : « {nouveau.titre} ».')
        return redirect('surveys:detail', slug=nouveau.slug)


class SurveyArchiveView(RequireCreateurMixin, View):
    def post(self, request, slug):
        sondage = get_object_or_404(Sondage, slug=slug)
        if sondage.createur != request.user and not getattr(getattr(request.user, 'profil', None), 'est_admin', lambda: False)():
            return HttpResponseForbidden()
        if sondage.est_archive:
            sondage.desarchiver()
            messages.success(request, f'Sondage « {sondage.titre} » désarchivé.')
        else:
            sondage.archiver()
            messages.success(request, f'Sondage « {sondage.titre} » archivé.')
        return redirect('surveys:detail', slug=sondage.slug)


class SurveyExportCSVView(RequireCreateurMixin, View):
    def get(self, request, slug):
        sondage = get_object_or_404(Sondage, slug=slug)
        if sondage.createur != request.user and not getattr(getattr(request.user, 'profil', None), 'est_admin', lambda: False)():
            return HttpResponseForbidden()
        return sondage.exporter_csv()


class SurveyExportXLSXView(RequireCreateurMixin, View):
    def get(self, request, slug):
        sondage = get_object_or_404(Sondage, slug=slug)
        if sondage.createur != request.user and not getattr(getattr(request.user, 'profil', None), 'est_admin', lambda: False)():
            return HttpResponseForbidden()
        return sondage.exporter_excel()


class SurveyShareView(RequireCreateurMixin, View):
    template_name = 'surveys/share.html'

    def get_sondage(self, request, slug):
        sondage = get_object_or_404(Sondage, slug=slug)
        if sondage.createur != request.user and not getattr(getattr(request.user, 'profil', None), 'est_admin', lambda: False)():
            raise PermissionDenied
        return sondage

    def get(self, request, slug):
        from django.shortcuts import render
        sondage = self.get_sondage(request, slug)
        lien_actif = sondage.liens.filter(est_actif=True).first()
        return render(request, self.template_name, {
            'sondage': sondage,
            'liens': sondage.liens.order_by('-cree_le'),
            'lien_actif': lien_actif,
            'code_integration': sondage.obtenir_code_integration(),
        })

    def post(self, request, slug):
        sondage = self.get_sondage(request, slug)
        action = request.POST.get('action')
        if action == 'nouveau_lien':
            LienPartage.objects.create(sondage=sondage)
            messages.success(request, 'Nouveau lien de partage créé.')
        elif action == 'desactiver':
            jeton = request.POST.get('jeton')
            lien = get_object_or_404(LienPartage, jeton=jeton, sondage=sondage)
            lien.desactiver()
            messages.success(request, 'Lien désactivé.')
        return redirect('surveys:share', slug=sondage.slug)


def _get_sondage_or_403(slug, user):
    """Récupère un sondage par slug avec bypass admin, sinon 403."""
    sondage = get_object_or_404(Sondage, slug=slug)
    profil = getattr(user, 'profil', None)
    if sondage.createur != user and not (profil and profil.est_admin()):
        raise PermissionDenied
    return sondage


class SectionCreateView(RequireCreateurMixin, View):
    def post(self, request, slug):
        sondage = _get_sondage_or_403(slug, request.user)
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.sondage = sondage
            max_ordre = sondage.sections.order_by('-ordre').values_list('ordre', flat=True).first()
            section.ordre = (max_ordre or 0) + 1
            section.save()
        else:
            messages.error(request, 'Titre de section requis.')
        return redirect('surveys:builder', slug=slug)


class SectionDeleteView(RequireCreateurMixin, View):
    def post(self, request, slug, section_id):
        sondage = _get_sondage_or_403(slug, request.user)
        section = get_object_or_404(SectionSondage, pk=section_id, sondage=sondage)
        if sondage.sections.count() <= 1:
            messages.error(request, 'Un sondage doit avoir au moins une section.')
        else:
            section.delete()
            messages.success(request, 'Section supprimée.')
        return redirect('surveys:builder', slug=slug)


class QuestionCreateView(RequireCreateurMixin, View):
    def post(self, request, slug, section_id):
        sondage = _get_sondage_or_403(slug, request.user)
        section = get_object_or_404(SectionSondage, pk=section_id, sondage=sondage)
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.section = section
            max_ordre = section.questions.order_by('-ordre').values_list('ordre', flat=True).first()
            question.ordre = (max_ordre or 0) + 1
            condition_choix_id = request.POST.get('condition_choix', '').strip()
            if condition_choix_id:
                question.condition_choix = get_object_or_404(
                    Choix, pk=condition_choix_id,
                    question__section__sondage=sondage
                )
            question.save()
            choix_data = request.POST.get('choix_json', '').strip()
            if choix_data:
                try:
                    for i, texte in enumerate(json.loads(choix_data)):
                        if texte.strip():
                            Choix.objects.create(question=question, texte=texte.strip(), ordre=i)
                except (json.JSONDecodeError, TypeError):
                    pass
            messages.success(request, 'Question ajoutée.')
        else:
            messages.error(request, f'Erreur : {form.errors}')
        return redirect('surveys:builder', slug=slug)


class QuestionDeleteView(RequireCreateurMixin, View):
    def post(self, request, slug, question_id):
        sondage = _get_sondage_or_403(slug, request.user)
        question = get_object_or_404(Question, pk=question_id, section__sondage=sondage)
        question.delete()
        messages.success(request, 'Question supprimée.')
        return redirect('surveys:builder', slug=slug)
