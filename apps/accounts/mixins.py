from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import Profil


class RequireCreateurMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        profil, _ = Profil.objects.get_or_create(utilisateur=request.user)
        if not profil.est_createur():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class RequireAdminMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        profil, _ = Profil.objects.get_or_create(utilisateur=request.user)
        if not profil.est_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
