from django import forms
from .models import DossierMedical
from apps.patients.models import Patient

class DossierMedicalForm(forms.ModelForm):
    # Champ pour sélectionner ou créer un patient
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all(),
        label="Patient",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = DossierMedical
        fields = [
            'patient', 'date_consultation', 'motif_consultation',
            'symptomes', 'temperature', 'tension_arterielle', 'poids', 'taille',
            'diagnostic', 'diagnostic_differentiel', 'examens_complementaires',
            'prescription', 'posologie', 'notes_medicales', 'recommandations',
            'date_prochain_rdv', 'urgence', 'statut'
        ]
        widgets = {
            'date_consultation': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'date_prochain_rdv': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'motif_consultation': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'symptomes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'temperature': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'tension_arterielle': forms.TextInput(attrs={'placeholder': '120/80', 'class': 'form-control'}),
            'poids': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'taille': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'diagnostic': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'diagnostic_differentiel': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'examens_complementaires': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'prescription': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'posologie': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes_medicales': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'recommandations': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'urgence': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }