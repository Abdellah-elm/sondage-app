from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Utilisateur, Profil


class InscriptionForm(UserCreationForm):
    prenom = forms.CharField(max_length=100, label='Prénom')
    nom = forms.CharField(max_length=100, label='Nom')
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = Utilisateur
        fields = ['username', 'prenom', 'nom', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('prenom', css_class='col-md-6'),
                Column('nom', css_class='col-md-6'),
            ),
            'username', 'email', 'password1', 'password2',
            Submit('submit', "S'inscrire", css_class='btn btn-primary w-100 mt-3'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.prenom = self.cleaned_data['prenom']
        user.nom = self.cleaned_data['nom']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ConnexionForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username', 'password',
            Submit('submit', 'Se connecter', css_class='btn btn-primary w-100 mt-3'),
        )


class ProfilForm(forms.ModelForm):
    prenom = forms.CharField(max_length=100, label='Prénom')
    nom = forms.CharField(max_length=100, label='Nom')
    email = forms.EmailField(label='Email')

    class Meta:
        model = Profil
        fields = ['biographie', 'avatar', 'organisation']

    def __init__(self, *args, **kwargs):
        self.utilisateur = kwargs.pop('utilisateur', None)
        super().__init__(*args, **kwargs)
        if self.utilisateur:
            self.fields['prenom'].initial = self.utilisateur.prenom
            self.fields['nom'].initial = self.utilisateur.nom
            self.fields['email'].initial = self.utilisateur.email
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('prenom', css_class='col-md-6'), Column('nom', css_class='col-md-6')),
            'email', 'organisation', 'biographie', 'avatar',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary mt-3'),
        )

    def save(self, commit=True):
        profil = super().save(commit=False)
        if self.utilisateur:
            self.utilisateur.prenom = self.cleaned_data['prenom']
            self.utilisateur.nom = self.cleaned_data['nom']
            self.utilisateur.email = self.cleaned_data['email']
            self.utilisateur.save()
        if commit:
            profil.save()
        return profil


class AdminRoleForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['role']
