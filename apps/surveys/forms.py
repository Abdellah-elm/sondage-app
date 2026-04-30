from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Div, HTML
from .models import Sondage, SectionSondage, Question


class SondageForm(forms.ModelForm):
    mot_de_passe_brut = forms.CharField(
        required=False, widget=forms.PasswordInput,
        label='Mot de passe (laisser vide = pas de protection)'
    )

    class Meta:
        model = Sondage
        fields = [
            'titre', 'description', 'theme', 'est_anonyme', 'date_limite',
            'duree_limite_minutes', 'max_reponses', 'autoriser_integration', 'est_modele',
        ]
        widgets = {
            'date_limite': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_limite'].input_formats = ['%Y-%m-%dT%H:%M']
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'titre',
            'description',
            Row(
                Column('theme', css_class='col-md-6'),
                Column('mot_de_passe_brut', css_class='col-md-6'),
            ),
            Row(
                Column('date_limite', css_class='col-md-4'),
                Column('duree_limite_minutes', css_class='col-md-4'),
                Column('max_reponses', css_class='col-md-4'),
            ),
            Row(
                Column('est_anonyme', css_class='col-md-4'),
                Column('autoriser_integration', css_class='col-md-4'),
                Column('est_modele', css_class='col-md-4'),
            ),
        )

    def save(self, commit=True):
        sondage = super().save(commit=False)
        mdp = self.cleaned_data.get('mot_de_passe_brut', '').strip()
        if mdp:
            sondage.definir_mot_de_passe(mdp)
        elif not mdp and not self.instance.pk:
            sondage.mot_de_passe = ''
        if commit:
            sondage.save()
        return sondage


class SectionForm(forms.ModelForm):
    class Meta:
        model = SectionSondage
        fields = ['titre', 'description']  # ordre calculé dans la vue
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'texte', 'type_question', 'est_obligatoire',
            'echelle_min', 'echelle_max', 'libelle_min', 'libelle_max',
        ]  # ordre et condition_choix gérés dans la vue
        widgets = {'texte': forms.Textarea(attrs={'rows': 2})}


