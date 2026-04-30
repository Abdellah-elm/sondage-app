from django.db import models


class Notification(models.Model):
    TYPE_NOUVELLE_REPONSE = 'nouvelle_reponse'
    TYPE_SONDAGE_EXPIRE = 'sondage_expire'
    TYPES = [
        (TYPE_NOUVELLE_REPONSE, 'Nouvelle réponse'),
        (TYPE_SONDAGE_EXPIRE, 'Sondage expiré'),
    ]

    utilisateur = models.ForeignKey(
        'accounts.Utilisateur', on_delete=models.CASCADE, related_name='notifications'
    )
    sondage = models.ForeignKey(
        'surveys.Sondage', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='notifications'
    )
    message = models.CharField(max_length=500)
    type_notification = models.CharField(max_length=30, choices=TYPES)
    est_lu = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-cree_le']

    def __str__(self):
        return f'{self.get_type_notification_display()} — {self.utilisateur.username}'

    def marquer_comme_lu(self):
        self.est_lu = True
        self.save()
