from .models import Notification


def notifications_context(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            utilisateur=request.user,
            est_lu=False
        ).count()
        return {'notifications_non_lues': count}
    return {'notifications_non_lues': 0}
