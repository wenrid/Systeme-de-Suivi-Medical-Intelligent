from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('medecin', 'Médecin'),
        ('analyste', 'Analyste de santé'),
        ('admin', 'Administrateur'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='medecin')
    numero_ordre = models.CharField(max_length=20, blank=True, help_text="Numéro d'ordre professionnel")
    specialite = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    is_active_medical = models.BooleanField(default=True, help_text="Autorisé à exercer")
    
    class Meta:
        db_table = 'auth_users_medical'
        verbose_name = 'Utilisateur médical'
        verbose_name_plural = 'Utilisateurs médicaux'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_medecin(self):
        return self.role == 'medecin'
    
    @property
    def is_analyste(self):
        return self.role == 'analyste'
    
    @property
    def is_admin_medical(self):
        return self.role == 'admin'