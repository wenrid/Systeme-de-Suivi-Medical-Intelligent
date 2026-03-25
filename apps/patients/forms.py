from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            # Identité
            'nom', 'prenom', 'date_naissance', 'lieu_naissance', 
            'sexe', 'groupe_sanguin', 'photo', 'photo_carte_identite',
            
            # Contact
            'telephone', 'telephone_secondaire', 'email', 
            'adresse', 'quartier_commune', 'ville',
            
            # Contact d'urgence
            'contact_urgence_nom', 'contact_urgence_lien', 'contact_urgence_telephone',
            
            # Antécédents médicaux
            'allergies', 'diabete', 'hypertension', 'asthme', 
            'epilepsie', 'drepanocytose', 'vih', 'autre_maladie_chronique',
            'traitements_en_cours', 'antecedents_chirurgicaux', 
            'antecedents_medicaux', 'notes_medicales',
        ]
        
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'groupe_sanguin': forms.Select(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone_secondaire': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quartier_commune': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_urgence_nom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_urgence_lien': forms.Select(attrs={'class': 'form-control'}),
            'contact_urgence_telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'autre_maladie_chronique': forms.TextInput(attrs={'class': 'form-control'}),
            'traitements_en_cours': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'antecedents_chirurgicaux': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'antecedents_medicaux': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes_medicales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'date_naissance': 'Date de naissance',
            'lieu_naissance': 'Lieu de naissance',
            'sexe': 'Sexe',
            'groupe_sanguin': 'Groupe sanguin',
            'photo': 'Photo',
            'photo_carte_identite': "Photo carte d'identité",
            'telephone': 'Téléphone',
            'telephone_secondaire': 'Téléphone secondaire',
            'email': 'Email',
            'adresse': 'Adresse',
            'quartier_commune': 'Quartier/Commune',
            'ville': 'Ville',
            'contact_urgence_nom': "Nom du contact d'urgence",
            'contact_urgence_lien': 'Lien',
            'contact_urgence_telephone': 'Téléphone',
            'allergies': 'Allergies connues',
            'diabete': 'Diabète',
            'hypertension': 'Hypertension',
            'asthme': 'Asthme',
            'epilepsie': 'Épilepsie',
            'drepanocytose': 'Drépanocytose',
            'vih': 'VIH',
            'autre_maladie_chronique': 'Autre maladie chronique',
            'traitements_en_cours': 'Traitements en cours',
            'antecedents_chirurgicaux': 'Antécédents chirurgicaux',
            'antecedents_medicaux': 'Antécédents médicaux',
            'notes_medicales': 'Notes médicales',
        }