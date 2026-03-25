from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['code_patient', 'nom', 'prenom', 'date_naissance', 'sexe', 'telephone', 'statut']
    list_filter = ['sexe', 'statut', 'date_creation']
    search_fields = ['code_patient', 'nom', 'prenom', 'telephone', 'email']
    readonly_fields = ['code_patient', 'age', 'date_creation', 'date_modification']
    
    fieldsets = (
        ('Identité', {
            'fields': ('code_patient', 'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe', 'groupe_sanguin', 'photo', 'photo_carte_identite')
        }),
        ('Contact', {
            'fields': ('telephone', 'telephone_secondaire', 'email', 'adresse', 'quartier_commune', 'ville')
        }),
        ('Contact d\'urgence', {
            'fields': ('contact_urgence_nom', 'contact_urgence_lien', 'contact_urgence_telephone')
        }),
        ('Antécédents médicaux', {
            'fields': ('allergies', 'diabete', 'hypertension', 'asthme', 'epilepsie', 'drepanocytose', 'vih', 'autre_maladie_chronique', 'traitements_en_cours', 'antecedents_chirurgicaux', 'antecedents_medicaux', 'notes_medicales')
        }),
        ('Statut', {
            'fields': ('statut', 'valide_par', 'date_validation')
        }),
        ('Métadonnées', {
            'fields': ('age', 'date_creation', 'date_modification', 'cree_par'),
            'classes': ('collapse',)
        }),
    )