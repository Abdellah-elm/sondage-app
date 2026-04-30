from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.views import View
from apps.accounts.mixins import RequireAdminMixin, RequireCreateurMixin
from apps.accounts.models import Utilisateur, Profil
from apps.accounts.forms import AdminRoleForm
from apps.surveys.models import Sondage, LienPartage
from apps.responses.models import Soumission
from apps.analytics.models import StatistiqueSondage
from .models import Notification



class SmartDashboardView(LoginRequiredMixin, View):
    """Redirige vers le bon dashboard selon le rôle."""
    def get(self, request):
        profil, _ = Profil.objects.get_or_create(utilisateur=request.user)
        if profil.est_admin():
            return redirect('dashboard:admin')
        if profil.est_createur():
            return redirect('dashboard:index')
        return redirect('dashboard:participant')



class DashboardView(RequireCreateurMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profil, _ = Profil.objects.get_or_create(utilisateur=user)

        sondages = Sondage.objects.filter(createur=user)
        context.update({
            'profil': profil,
            'nb_sondages': sondages.count(),
            'nb_actifs': sondages.filter(est_actif=True, est_archive=False).count(),
            'total_reponses': Soumission.objects.filter(
                sondage__createur=user, est_complete=True).count(),
            'notifications_non_lues': Notification.objects.filter(
                utilisateur=user, est_lu=False).count(),
            'sondages_recents': sondages.order_by('-cree_le')[:5],
            'soumissions_recentes': Soumission.objects.filter(
                sondage__createur=user, est_complete=True
            ).select_related('sondage', 'repondant').order_by('-termine_le')[:10],
        })
        return context



class ParticipantDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/participant.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        profil, _ = Profil.objects.get_or_create(utilisateur=request.user)
        if profil.est_createur():
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        liens_actifs = LienPartage.objects.filter(
            est_actif=True,
            sondage__est_actif=True,
            sondage__est_archive=False,
            sondage__est_modele=False,
        ).select_related('sondage').order_by('-cree_le')[:6]

        soumis_ids = Soumission.objects.filter(
            repondant=user, est_complete=True
        ).values_list('sondage_id', flat=True)

        participations = Soumission.objects.filter(
            repondant=user, est_complete=True
        ).select_related('sondage').order_by('-termine_le')[:5]

        context.update({
            'liens_recents': liens_actifs,
            'soumis_ids': list(soumis_ids),
            'participations': participations,
            'nb_participations': Soumission.objects.filter(
                repondant=user, est_complete=True).count(),
            'notifications_non_lues': Notification.objects.filter(
                utilisateur=user, est_lu=False).count(),
        })
        return context


class SondagesDisponiblesView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/sondages_disponibles.html'
    context_object_name = 'liens'
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        profil, _ = Profil.objects.get_or_create(utilisateur=request.user)
        if profil.est_createur():
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        qs = LienPartage.objects.filter(
            est_actif=True,
            sondage__est_actif=True,
            sondage__est_archive=False,
            sondage__est_modele=False,
        ).select_related('sondage').order_by('-cree_le')
        if q:
            qs = qs.filter(sondage__titre__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        soumis_ids = list(
            Soumission.objects.filter(
                repondant=self.request.user, est_complete=True
            ).values_list('sondage_id', flat=True)
        )
        context['soumis_ids'] = soumis_ids
        context['q'] = self.request.GET.get('q', '')
        return context


class MonHistoriqueView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/mon_historique.html'
    context_object_name = 'participations'
    paginate_by = 15

    def get(self, request, *args, **kwargs):
        profil, _ = Profil.objects.get_or_create(utilisateur=request.user)
        if profil.est_createur():
            return redirect('dashboard:index')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Soumission.objects.filter(
            repondant=self.request.user
        ).select_related('sondage').order_by('-commence_le')



class NotificationsView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            utilisateur=self.request.user
        ).select_related('sondage').order_by('-cree_le')

    def get(self, request, *args, **kwargs):
        Notification.objects.filter(utilisateur=request.user, est_lu=False).update(est_lu=True)
        return super().get(request, *args, **kwargs)


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, utilisateur=request.user)
        notif.marquer_comme_lu()
        return redirect('dashboard:notifications')



class AdminDashboardView(RequireAdminMixin, TemplateView):
    template_name = 'dashboard/admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_utilisateurs': Utilisateur.objects.count(),
            'total_sondages': Sondage.objects.count(),
            'total_reponses': Soumission.objects.filter(est_complete=True).count(),
            'nb_visiteurs': Profil.objects.filter(role='visiteur').exclude(utilisateur__is_superuser=True).count(),
            'nb_createurs': Profil.objects.filter(role='createur').count(),
            'sondages_recents': Sondage.objects.select_related('createur').order_by('-cree_le')[:10],
            'utilisateurs_recents': Utilisateur.objects.select_related('profil').order_by('-date_joined')[:10],
        })
        return context


class AdminUsersView(RequireAdminMixin, ListView):
    template_name = 'dashboard/admin_users.html'
    context_object_name = 'utilisateurs'
    paginate_by = 20

    def get_queryset(self):
        qs = Utilisateur.objects.select_related('profil').order_by('-date_joined')
        q = self.request.GET.get('q', '')
        role = self.request.GET.get('role', '')
        if q:
            qs = qs.filter(username__icontains=q)
        if role:
            qs = qs.filter(profil__role=role)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['role_filtre'] = self.request.GET.get('role', '')
        return context


class AdminChangeRoleView(RequireAdminMixin, View):
    def post(self, request, pk):
        utilisateur = get_object_or_404(Utilisateur, pk=pk)
        if utilisateur == request.user or utilisateur.is_superuser:
            messages.error(request, 'Impossible de modifier ce compte.')
            return redirect('dashboard:admin_users')
        profil, _ = Profil.objects.get_or_create(utilisateur=utilisateur)
        nouveau_role = request.POST.get('role', '').strip()
        roles_valides = [r[0] for r in Profil.ROLES]
        if nouveau_role in roles_valides:
            profil.role = nouveau_role
            profil.save()
            messages.success(
                request,
                f'✓ {utilisateur.username} est maintenant « {profil.get_role_display()} ».'
            )
        elif nouveau_role:
            messages.error(request, f'Rôle invalide : {nouveau_role}')
        return redirect('dashboard:admin_users')


class AdminSurveysView(RequireAdminMixin, ListView):
    template_name = 'dashboard/admin_surveys.html'
    context_object_name = 'sondages'
    paginate_by = 20

    def get_queryset(self):
        qs = Sondage.objects.select_related('createur').order_by('-cree_le')
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(titre__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context
