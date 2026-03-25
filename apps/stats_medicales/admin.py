from django.contrib import admin
from .models import AnalyseStatistique, RapportAnnuel

@admin.register(AnalyseStatistique)
class AnalyseStatistiqueAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type_analyse', 'created_by', 'date_creation', 'is_public']
    list_filter = ['type_analyse', 'is_public', 'date_creation']
    search_fields = ['titre', 'description']
    readonly_fields = ['id', 'date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('type_analyse', 'titre', 'description', 'is_public')
        }),
        ('Données', {
            'fields': ('parametres', 'resultats'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_by', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

@admin.register(RapportAnnuel)
class RapportAnnuelAdmin(admin.ModelAdmin):
    list_display = ['annee', 'total_patients', 'total_consultations', 'created_by', 'date_generation']
    list_filter = ['annee', 'date_generation']
    readonly_fields = ['date_generation']
    
    fieldsets = (
        ('Rapport', {
            'fields': ('annee', 'created_by')
        }),
        ('Statistiques globales', {
            'fields': ('total_patients', 'total_consultations')
        }),
        ('Données détaillées', {
            'fields': ('pathologies_principales', 'statistiques_age', 'statistiques_sexe'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('date_generation',),
            'classes': ('collapse',)
        }),
    )