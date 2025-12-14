# maison_app/forms.py
from django import forms
from .models import Depense, Budget, CategorieDepense

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••', 'id': 'id_password'})
    )

class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = ['description', 'montant', 'categorie', 'date_depense', 'notes']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'date_depense': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes...'}),
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['categorie', 'montant_limite', 'periode']
        widgets = {
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'montant_limite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'periode': forms.Select(attrs={'class': 'form-select'}),
        }