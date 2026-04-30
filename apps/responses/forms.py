from django import forms
from apps.surveys.models import Question


class DynamicResponseForm(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for question in questions:
            field_name = f'q_{question.pk}'
            is_required = question.est_obligatoire and not question.condition_choix
            if question.type_question == Question.TYPE_TEXTE:
                self.fields[field_name] = forms.CharField(
                    label=question.texte,
                    required=is_required,
                    widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                )
            elif question.type_question == Question.TYPE_ECHELLE:
                self.fields[field_name] = forms.IntegerField(
                    label=question.texte,
                    required=is_required,
                    min_value=question.echelle_min,
                    max_value=question.echelle_max,
                    widget=forms.NumberInput(attrs={
                        'type': 'range',
                        'class': 'form-range',
                        'min': question.echelle_min,
                        'max': question.echelle_max,
                        'oninput': f'document.getElementById("val_{question.pk}").textContent=this.value',
                    }),
                )
            elif question.type_question == Question.TYPE_CHOIX_UNIQUE:
                self.fields[field_name] = forms.ModelChoiceField(
                    queryset=question.obtenir_choix(),
                    label=question.texte,
                    required=is_required,
                    empty_label='— Choisissez —',
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                )
            elif question.type_question == Question.TYPE_CHOIX_MULTIPLE:
                self.fields[field_name] = forms.ModelMultipleChoiceField(
                    queryset=question.obtenir_choix(),
                    label=question.texte,
                    required=is_required,
                    widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                )


class PasswordSondageForm(forms.Form):
    mot_de_passe = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le mot de passe'}),
    )
