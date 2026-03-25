from django.db import models
from django.utils import timezone
import os

def patient_photo_path(instance, filename):
    """Chemin pour la photo du patient"""
    ext = filename.split('.')[-1]
    filename = f"patient_{instance.id}.{ext}"
    return os.path.join('patients/photos', filename)

def patient_id_card_path(instance, filename):
    """Chemin pour la carte d'identité"""
    ext = filename.split('.')[-1]
    filename = f"id_card_{instance.id}.{ext}"
    return os.path.join('patients/id_cards', filename)

class Patient(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    GROUPE_SANGUIN_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    LIEN_URGENCE_CHOICES = [
        ('parent', 'Parent'),
        ('conjoint', 'Conjoint(e)'),
        ('enfant', 'Enfant'),
        ('ami', 'Ami(e)'),
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('en_attente', 'En attente de validation'),
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
    ]
    
    # Code patient unique
    code_patient = models.CharField(max_length=20, unique=True, blank=True, help_text="Format: P{ANNÉE}{MOIS}{NUMÉRO}")
    
    # Section 1 : Identité
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=200, blank=True)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, blank=True)
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_SANGUIN_CHOICES, blank=True)
    photo = models.ImageField(upload_to=patient_photo_path, blank=True, null=True)
    photo_carte_identite = models.ImageField(upload_to=patient_id_card_path, blank=True, null=True)
    
    # Section 2 : Contact
    telephone = models.CharField(max_length=20, blank=True)
    telephone_secondaire = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    quartier_commune = models.CharField(max_length=100, blank=True)
    ville = models.CharField(max_length=100, default='Kinshasa', blank=True)
    
    # Contact d'urgence
    contact_urgence_nom = models.CharField(max_length=100, blank=True)
    contact_urgence_lien = models.CharField(max_length=20, choices=LIEN_URGENCE_CHOICES, blank=True)
    contact_urgence_telephone = models.CharField(max_length=20, blank=True)
    
    # Section 3 : Antécédents médicaux
    allergies = models.TextField(blank=True, help_text="Allergies connues")
    
    # Maladies chroniques (checkboxes)
    diabete = models.BooleanField(default=False)
    hypertension = models.BooleanField(default=False)
    asthme = models.BooleanField(default=False)
    epilepsie = models.BooleanField(default=False)
    drepanocytose = models.BooleanField(default=False)
    vih = models.BooleanField(default=False)
    autre_maladie_chronique = models.CharField(max_length=200, blank=True)
    
    traitements_en_cours = models.TextField(blank=True)
    antecedents_chirurgicaux = models.TextField(blank=True)
    antecedents_medicaux = models.TextField(blank=True)
    notes_medicales = models.TextField(blank=True, help_text="Notes importantes")
    
    # Statut et validation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    valide_par = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='patients_valides')
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='patients_crees')
    
    class Meta:
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.code_patient} - {self.nom_complet}"
    
    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenom}"
    
    @property
    def age(self):
        """Calcule l'âge du patient"""
        today = timezone.now().date()
        age = today.year - self.date_naissance.year
        if today.month < self.date_naissance.month or (today.month == self.date_naissance.month and today.day < self.date_naissance.day):
            age -= 1
        return age
    
    def save(self, *args, **kwargs):
        """Génère automatiquement le code patient si non existant"""
        if not self.code_patient:
            self.code_patient = self.generer_code_patient()
        super().save(*args, **kwargs)
    
    def generer_code_patient(self):
        """Génère un code patient au format P{ANNÉE}{MOIS}{NUMÉRO}"""
        now = timezone.now()
        prefix = f"P{now.year}{now.month:02d}"
        
        # Trouver le dernier numéro du mois
        last_patient = Patient.objects.filter(
            code_patient__startswith=prefix
        ).order_by('-code_patient').first()
        
        if last_patient:
            last_number = int(last_patient.code_patient[-3:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:03d}"
    
    @property
    def maladies_chroniques_list(self):
        """Retourne la liste des maladies chroniques"""
        maladies = []
        if self.diabete:
            maladies.append('Diabète')
        if self.hypertension:
            maladies.append('Hypertension')
        if self.asthme:
            maladies.append('Asthme')
        if self.epilepsie:
            maladies.append('Épilepsie')
        if self.drepanocytose:
            maladies.append('Drépanocytose')
        if self.vih:
            maladies.append('VIH')
        if self.autre_maladie_chronique:
            maladies.append(self.autre_maladie_chronique)
        return maladies