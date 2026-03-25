"""
Script de génération de données de test pour le SSMI
Crée des consultations (dossiers médicaux) antidatées pour tester les modules IA
"""

import os
import django
from datetime import datetime, timedelta
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_system.settings')
django.setup()

from apps.patients.models import Patient
from apps.dossiers.models import DossierMedical
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# ========== CONFIGURATION ==========
NB_JOURS_HISTORIQUE = 30
MIN_CONSULTATIONS_PAR_JOUR = 2
MAX_CONSULTATIONS_PAR_JOUR = 8

MALADIES = [
    'Grippe',
    'Paludisme', 
    'Hypertension',
    'Diabète',
    'Asthme',
    'Bronchite',
    'Gastro-entérite',
    'Angine'
]

POIDS_MALADIES = {
    'Grippe': 30,
    'Paludisme': 25,
    'Hypertension': 20,
    'Diabète': 10,
    'Asthme': 5,
    'Bronchite': 5,
    'Gastro-entérite': 3,
    'Angine': 2
}

# ========== VÉRIFICATIONS ==========
print("=" * 60)
print("GENERATION DE DONNEES TEST POUR LE SSMI")
print("=" * 60)

patients = list(Patient.objects.all())
medecins = list(User.objects.filter(role='medecin'))

if not medecins:
    print("\nERREUR : Aucun medecin trouve !")
    exit(1)

if len(patients) < 3:
    print(f"\nERREUR : Seulement {len(patients)} patient(s)")
    exit(1)

print(f"\n{len(patients)} patients trouves")
print(f"{len(medecins)} medecin(s) trouve(s)")
print(f"\nGeneration sur {NB_JOURS_HISTORIQUE} jours...")

# ========== FONCTION ==========
def choisir_maladie():
    maladies_liste = []
    for maladie, poids in POIDS_MALADIES.items():
        maladies_liste.extend([maladie] * poids)
    return random.choice(maladies_liste)

# ========== GÉNÉRATION ==========
consultations_creees = 0
consultations_par_maladie = {maladie: 0 for maladie in MALADIES}
consultations_par_jour = []

print("\nGeneration en cours...")

for i in range(NB_JOURS_HISTORIQUE):
    date_consultation = timezone.now() - timedelta(days=i)
    
    if random.random() < 0.2:
        nb_consultations = random.randint(MAX_CONSULTATIONS_PAR_JOUR - 2, MAX_CONSULTATIONS_PAR_JOUR)
    else:
        nb_consultations = random.randint(MIN_CONSULTATIONS_PAR_JOUR, MAX_CONSULTATIONS_PAR_JOUR - 2)
    
    consultations_jour = 0
    
    for j in range(nb_consultations):
        patient = random.choice(patients)
        medecin = random.choice(medecins)
        maladie = choisir_maladie()
        
        # Créer un dossier médical (= consultation)
        DossierMedical.objects.create(
            patient=patient,
            medecin=medecin,
            date_consultation=date_consultation,
            motif_consultation=f"Symptomes de {maladie}",
            symptomes=f"Patient presente des symptomes de {maladie}",
            diagnostic=maladie,
            prescription=f"Traitement prescrit pour {maladie}",
            posologie="Selon prescription medicale",
            notes_medicales=f"Consultation test - Jour -{i}",
            urgence='faible' if random.random() < 0.7 else 'moyenne',
            statut='ouvert'
        )
        
        consultations_creees += 1
        consultations_par_maladie[maladie] += 1
        consultations_jour += 1
    
    consultations_par_jour.append(consultations_jour)
    
    if (i + 1) % 5 == 0:
        print(f"   {i + 1}/{NB_JOURS_HISTORIQUE} jours traites ({consultations_creees} consultations)")

# ========== STATISTIQUES ==========
print("\n" + "=" * 60)
print("GENERATION TERMINEE AVEC SUCCES !")
print("=" * 60)

print(f"\nSTATISTIQUES GLOBALES :")
print(f"   Total consultations : {consultations_creees}")
print(f"   Periode : {NB_JOURS_HISTORIQUE} jours")
print(f"   Moyenne : {consultations_creees/NB_JOURS_HISTORIQUE:.1f} consultations/jour")
print(f"   Minimum : {min(consultations_par_jour)} consultations/jour")
print(f"   Maximum : {max(consultations_par_jour)} consultations/jour")

print(f"\nREPARTITION PAR MALADIE :")
for maladie in sorted(consultations_par_maladie.keys(), 
                      key=lambda x: consultations_par_maladie[x], 
                      reverse=True):
    nb = consultations_par_maladie[maladie]
    if nb > 0:
        pourcentage = (nb / consultations_creees) * 100
        barre = '#' * int(pourcentage / 2)
        print(f"   {maladie:<20} : {nb:>3} cas ({pourcentage:>5.1f}%) {barre}")

print(f"\nREPARTITION PAR PATIENT (Top 5) :")
consultations_par_patient = {}
for dossier in DossierMedical.objects.filter(
    date_consultation__gte=timezone.now() - timedelta(days=NB_JOURS_HISTORIQUE)
):
    patient_nom = f"{dossier.patient.nom} {dossier.patient.prenom}"
    consultations_par_patient[patient_nom] = consultations_par_patient.get(patient_nom, 0) + 1

for patient_nom, nb in sorted(consultations_par_patient.items(), 
                               key=lambda x: x[1], 
                               reverse=True)[:5]:
    print(f"   {patient_nom:<30} : {nb} consultations")

print("\n" + "=" * 60)
print("PROCHAINES ETAPES :")
print("=" * 60)
print("\n1. Va sur le dashboard")
print("2. Clique sur : Analyses IA")
print("3. Clique sur : Prediction d'Epidemies")
print("4. Tu verras les graphiques et predictions !")
print("\n" + "=" * 60)