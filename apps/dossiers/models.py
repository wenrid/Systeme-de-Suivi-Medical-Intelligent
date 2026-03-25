from django.db import models
from django.conf import settings
from apps.patients.models import Patient
import uuid

class DossierMedical(models.Model):
    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('ferme', 'Fermé'),
        ('en_attente', 'En attente'),
        ('archive', 'Archivé'),
    ]
    
    URGENCE_CHOICES = [
        ('faible', 'Faible'),
        ('moyenne', 'Moyenne'),
        ('elevee', 'Élevée'),
        ('critique', 'Critique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dossiers')
    medecin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dossiers_crees')
    
    # Informations de consultation
    date_consultation = models.DateTimeField()
    motif_consultation = models.TextField(help_text="Raison de la visite")
    
    # Examen clinique
    symptomes = models.TextField(help_text="Liste des symptômes observés", blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="En °C")
    tension_arterielle = models.CharField(max_length=20, blank=True, help_text="Ex: 120/80")
    poids = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="En kg")
    taille = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="En cm")
    
    # Diagnostic et traitement
    diagnostic = models.TextField()
    diagnostic_differentiel = models.TextField(blank=True, help_text="Autres diagnostics possibles")
    examens_complementaires = models.TextField(blank=True, help_text="Examens demandés (radio, analyses, etc.)")
    prescription = models.TextField(blank=True, help_text="Médicaments prescrits")
    posologie = models.TextField(blank=True, help_text="Dosage et fréquence")
    
    # Suivi
    notes_medicales = models.TextField(blank=True)
    recommandations = models.TextField(blank=True, help_text="Conseils au patient")
    date_prochain_rdv = models.DateField(null=True, blank=True)
    urgence = models.CharField(max_length=20, choices=URGENCE_CHOICES, default='faible')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouvert')
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dossiers_medicaux'
        verbose_name = 'Dossier médical'
        verbose_name_plural = 'Dossiers médicaux'
        ordering = ['-date_consultation']
    
    def __str__(self):
        return f"Dossier {self.patient.nom_complet} - {self.date_consultation.strftime('%d/%m/%Y')}"
    
    @property
    def imc(self):
        """Calcule l'IMC si poids et taille disponibles"""
        if self.poids and self.taille:
            taille_m = float(self.taille) / 100
            return round(float(self.poids) / (taille_m ** 2), 2)
        return None