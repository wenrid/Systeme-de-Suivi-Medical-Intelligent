from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()

class AnalyseStatistique(models.Model):
    TYPE_CHOICES = [
        ('age_groups', 'Analyse par tranche d\'âge'),
        ('pathologies', 'Pathologies fréquentes'),
        ('geographic', 'Répartition géographique'),
        ('annual_report', 'Rapport annuel'),
        ('gender_analysis', 'Analyse par sexe'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_analyse = models.CharField(max_length=50, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    parametres = models.JSONField(default=dict, help_text="Paramètres de l'analyse")
    resultats = models.JSONField(default=dict, help_text="Résultats de l'analyse")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses_creees')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True, help_text="Visible par tous les analystes")
    
    class Meta:
        db_table = 'analyses_statistiques'
        verbose_name = 'Analyse statistique'
        verbose_name_plural = 'Analyses statistiques'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} ({self.get_type_analyse_display()})"

class RapportAnnuel(models.Model):
    annee = models.PositiveIntegerField()
    total_patients = models.PositiveIntegerField()
    total_consultations = models.PositiveIntegerField()
    pathologies_principales = models.JSONField(default=list)
    statistiques_age = models.JSONField(default=dict)
    statistiques_sexe = models.JSONField(default=dict)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_generation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rapports_annuels'
        verbose_name = 'Rapport annuel'
        verbose_name_plural = 'Rapports annuels'
        unique_together = ['annee']
    
    def __str__(self):
        return f"Rapport annuel {self.annee}"