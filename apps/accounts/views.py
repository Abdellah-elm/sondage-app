from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse_lazy
from .forms import InscriptionForm, ConnexionForm, ProfilForm
from .models import Utilisateur, Profil


def _redirect_apres_connexion(user, next_url=None, host=None, is_secure=False):
    
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url, allowed_hosts={host}, require_https=is_secure
    ):
        return redirect(next_url)
    profil, _ = Profil.objects.get_or_create(utilisateur=user)
    if profil.est_createur():
        return redirect('dashboard:index')
    return redirect('dashboard:participant')


class InscriptionView(View):
    template_name = 'accounts/inscription.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return _redirect_apres_connexion(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        from django.shortcuts import render
        return render(request, self.template_name, {'form': InscriptionForm()})

    def post(self, request):
        from django.shortcuts import render
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} ! Votre compte a été créé.')
            return _redirect_apres_connexion(user)
        return render(request, self.template_name, {'form': form})


class ConnexionView(TemplateView):
    template_name = 'accounts/connexion.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return _redirect_apres_connexion(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = form or ConnexionForm()
        return context

    def post(self, request):
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            return _redirect_apres_connexion(
                user,
                next_url=request.GET.get('next', ''),
                host=request.get_host(),
                is_secure=request.is_secure(),
            )
        return self.render_to_response(self.get_context_data(form=form))


class DeconnexionView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'Vous avez été déconnecté.')
        return redirect('accounts:connexion')

    def get(self, request):
        return redirect('accounts:connexion')


class ProfilView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profil.html'

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        profil, _ = Profil.objects.get_or_create(utilisateur=self.request.user)
        context['profil'] = profil
        context['form'] = form or ProfilForm(instance=profil, utilisateur=self.request.user)
        context['sondages_crees'] = self.request.user.obtenir_sondages_crees()[:5]
        context['participations'] = self.request.user.obtenir_historique_participations()[:5]
        return context

    def post(self, request):
        profil, _ = Profil.objects.get_or_create(utilisateur=request.user)
        form = ProfilForm(request.POST, request.FILES, instance=profil, utilisateur=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('accounts:profil')
        return self.render_to_response(self.get_context_data(form=form))
