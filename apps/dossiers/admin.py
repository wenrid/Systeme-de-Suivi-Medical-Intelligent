from django.contrib import admin
from .models import DossierMedical

@admin.register(DossierMedical)
class DossierMedicalAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medecin', 'date_consultation', 'statut']
    list_filter = ['statut', 'date_consultation', 'medecin']
    search_fields = ['patient__nom', 'patient__prenom', 'diagnostic']
    date_hierarchy = 'date_consultation'
    readonly_fields = ['id', 'date_creation', 'date_modification']
    
    fieldsets = (
        ('Patient et médecin', {
            'fields': ('patient', 'medecin')
        }),
        ('Consultation', {
            'fields': ('date_consultation', 'motif_consultation', 'diagnostic')
        }),
        ('Traitement', {
            'fields': ('prescription', 'notes_medicales')
        }),
        ('Statut', {
            'fields': ('statut',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )